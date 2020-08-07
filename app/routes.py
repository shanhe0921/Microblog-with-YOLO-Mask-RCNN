import os
import io
import PIL.Image
import hashlib
import time
import base64
import json
from flask import json, g
from app import app
from app.forms import LoginForm
from flask import render_template, flash, redirect, url_for, request, send_from_directory, make_response,\
abort, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from flask_uploads import UploadSet, configure_uploads, IMAGES,\
 patch_request_class
from app.models import User, Post, Image, DetectData
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from app import db, y, m, auth
from app.forms import RegistrationForm, EditProfileForm, UploadForm
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
detected = UploadSet('detected', IMAGES)
configure_uploads(app, detected)
patch_request_class(app)  # 文件大小限制，默认为16MB

@app.route('/')
@app.route('/index')
@login_required
def index():
	user = {'username': 'ZHENG'}
	posts = [
	{
		'author': {'username': 'Johm'},
		'body': 'Beautiful day in Portland!'
	},
	{
		'author': {'username': 'Susan'},
		'body': 'The Avengers movie was so cool!'
	}
    ]
	return render_template('index.html', title = 'Home Page', posts = posts)
	
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)
	
@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))
	
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/api/users/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'username': user.username})

@app.route('/api/users', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400)
    if User.query.filter_by(username=username).first() is not None:
        abort(400)
    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({ 'username': user.username }), 201, 
    {'Location': url_for('get_user', id = user.id, _external = True)}

@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})
    
@app.route('/api/resource')
@auth.login_required
def get_resource():
    return jsonify({'data': 'Hello, %s!' % g.user.username})

@app.route('/user/<username>')
@login_required
def user(username):
	user = User.query.filter_by(username=username).first_or_404()
	posts = [
		{'author':user, 'body':'Test post 1'},
		{'author':user, 'body':'Test post 2'}
	]
	return render_template('user.html', user=user, posts=posts)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)

@app.before_request
def before_request():
	if current_user.is_authenticated:
		current_user.last_seen = datetime.utcnow()
		db.session.commit()   

@app.route('/uploads', methods=['GET', 'POST'])
@login_required
def upload_file():
    form = UploadForm()
    if form.validate_on_submit():
        for filename in request.files.getlist('photo'):
            name = hashlib.md5((current_user.username + str(time.time())).encode('utf-8')).hexdigest()[:15]
            flash('Photo Upload Success!')
            file_path = photos.path(photos.save(filename, name=name + '.')).replace('\\','/')
            image = Image(address=file_path, upmaster=current_user)
            db.session.add(image)
            db.session.commit()
        success = True
    else:
        success = False
    return render_template('upload.html', form=form, success=success)
    
@app.route('/api/uploads', methods=['POST'])
@auth.login_required
def post_and_detect_api():
    # post a base64 type of image to server and save it.
    if not request.json:
        abort(400)
    image_width, image_height, image_bytes, detect_model = request.json.get('width'), request.json.get('height'), request.json.get('image'), request.json.get('model')
    imgdata = base64.b64decode(image_bytes)
    name = hashlib.md5((g.user.username + str(time.time())).encode('utf-8')).hexdigest()[:15]
    filename = app.config['UPLOADED_PHOTOS_DEST'] + '/' + name + '.png'
    with open(filename, 'wb') as f:
        f.write(imgdata)
    image = Image(address=filename, upmaster=g.user)
    db.session.add(image)
    db.session.commit()
    # detect the image and return detected data to client
    if detect_model == "YOLO":
        detected_image, listdata = y.detect_image(PIL.Image.open(photos.path(filename)))
        if len(listdata) == 0:
            return jsonify({'result': 'No object in the image'})
        filename = name + '_yolo_detected.png'
        filepath = os.path.join(app.config['UPLOADED_DETECTED_DEST'], filename)
        detected_image.save(filepath)
        for dictdata in listdata:
            data = DetectData(class_index=dictdata["class_index"], predicted_class=dictdata["predicted_class"], 
                            obj_score=dictdata["obj_score"], left=dictdata["left"], top=dictdata["top"], 
                            right=dictdata["right"], bottom=dictdata["bottom"], all_score=dictdata["all_score"],
                            multiple_obj=dictdata["multiple_obj"], fromwho=image
            )
            db.session.add(data)
            db.session.commit()
    elif detect_model == "MASK":
        pass
    else:
        abort(404)
    db.session.commit()
    return jsonify(listdata)
    

@auth.login_required
@app.route('/api/get_image/<int:image_id>', methods=['GET'])
def get_image_api(image_id):
    pass

@app.route('/manage')
@login_required
def manage_file():
    files_list = os.listdir(app.config['UPLOADED_PHOTOS_DEST'])
    return render_template('manage.html', files_list=files_list)


@app.route('/open/<filename>')
@login_required
def open_file(filename):
    file_url = photos.url(filename)
    return render_template('browser.html', file_url=file_url)

@app.route('/delete/<filename>')
@login_required
def delete_file(filename):
    file_path = photos.path(filename).replace('\\','/')
    print(file_path)
    image = Image.query.filter_by(address=file_path).first_or_404()
    db.session.delete(image)
    db.session.commit()
    os.remove(file_path)
    return redirect(url_for('manage_file'))

@app.route('/detect_yolo/<filename>')
@login_required 
def detect_image_yolo(filename):
    try:
        image, data = y.detect_image(PIL.Image.open(photos.path(filename)))
        #image.show()
        #DataBase madanashi
        filename = filename.split('.')[0] + '_yolo_detected.jpg'
        filepath = os.path.join(app.config['UPLOADED_DETECTED_DEST'], filename)
        image.save(filepath)
        file_url = detected.url(filename)
        print(file_url)
        flash('photo detect succeeded!')
    except:
        flash('photo detect failed')
    return render_template('detected.html', file_url=file_url)

@app.route('/detect_mask/<filename>')
@login_required 
def detect_image_mask(filename):
    # try:
    
    # DataBase madanashi
    # 
    filedir = app.config['UPLOADED_PHOTOS_DEST']
    savedir = app.config['UPLOADED_DETECTED_DEST']
    results = m.detect_image(filedir, savedir, filename)
    filename = filename.split('.')[0] + '_mask_detected.jpg'
    file_url = detected.url(filename)
    flash('photo detect succeeded!')
    # except:
        # flash('photo detect failed')
    return render_template('detected.html', file_url=file_url)