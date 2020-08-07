import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'shanhe'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['shanhe0522@outlook.com']
    YOLO_DIR = 'D:/yolo/keras-yolo3-master'
    MASK_DIR = 'D:/yolo/Mask_RCNN-master'
    UPLOADED_PHOTOS_DEST = 'C:/Users/ZHENG/Desktop/microblog/upload'
    UPLOADED_DETECTED_DEST = 'C:/Users/ZHENG/Desktop/microblog/detected'
    MAX_CONTENT_LENGTH = 16*1024*1024