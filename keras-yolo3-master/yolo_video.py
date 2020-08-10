import sys
import warnings
warnings.filterwarnings('ignore',category=FutureWarning)
import argparse
from yolo import YOLO, detect_video
from PIL import Image
import socket
import threading
import json
import time
from sys import argv
from base64 import b64encode

from pathlib import Path

ENCODING = 'utf-8'    # 指定编码形式
IMAGE_NAME = 'D:/ScreenShots/20191011110231.png'
HOST = '127.0.0.1'
PORT = 10086

# 作者用图像检测接口
def detect_img(yolo, key, img4unity):
    #img = input('Input image filename:')
    img = img4unity
    try:
        image = Image.open(img)
    except:
        print('Open Error! Try again!')
        exit()
    if key == 'L':
        d_start = time.time()
        r_image = yolo.detect_image(image)
        d_end = time.time()
        r_image.show()
        key = None
        end = time.time()
        print("Total time is:", end - start)

FLAGS = None

if __name__ == '__main__':
    # class YOLO defines the default value, so suppress any default here
    parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)
    '''
    Command line options
    '''
    parser.add_argument(
        '--model', type=str,
        help='path to model weight file, default ' + YOLO.get_defaults("model_path")
    )

    parser.add_argument(
        '--anchors', type=str,
        help='path to anchor definitions, default ' + YOLO.get_defaults("anchors_path")
    )

    parser.add_argument(
        '--classes', type=str,
        help='path to class definitions, default ' + YOLO.get_defaults("classes_path")
    )

    parser.add_argument(
        '--gpu_num', type=int,
        help='Number of GPU to use, default ' + str(YOLO.get_defaults("gpu_num"))
    )

    parser.add_argument(
        '--image', default=False, action="store_true",
        help='Image detection mode, will ignore all positional arguments'
    )
    '''
    Command line positional arguments -- for video detection mode
    '''
    parser.add_argument(
        "--input", nargs='?', type=str,required=False,default='./path2your_video',
        help = "Video input path"
    )

    parser.add_argument(
        "--output", nargs='?', type=str, default="",
        help = "[Optional] Video output path"
    )

    FLAGS = parser.parse_args()

    if FLAGS.image:
        """
        Image detection mode, disregard any remaining command line arguments
        """
        Y = YOLO()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST,PORT))
            s.listen()
            conn, addr = s.accept()
            with conn:
                print("Connected by", addr)
                while True:
                    message_b = conn.recv(1024)           
                    if not message_b:
                        break
                    message_s = message_b.decode(encoding = "utf-8")
                    print(message_s)
                    keycode, data = message_s.split(' ')
                    if keycode == 'E':
                        Y.close_session()
                        exit()
                    print(type(data), data)
                    print("Image detection mode")
                    if ("input" in FLAGS) and (keycode == "L"):
                        start = time.time()
                        print(" Ignoring remaining command line arguments: " + FLAGS.input + "," + FLAGS.output)
                        # 現在時刻ｔを取得
                        start = time.time()
                        while True:
                            try:
                               image, data_y = Y.detect_image(Image.open(data))
                               #print(type(image))
                               #print(type(data_y),data_y)
                               conn.send(data_y)
                               break
                            except Exception as e:
                               time.sleep(0.01)
                               
                               if time.time() - start > 5:
                                  raise Exception("5秒待機しましたが画像が開けませんでした")
                                  break
                        #image.save("result.jpg")
                        image.show()
                        #conn.send(b'hello')
    elif "input" in FLAGS:
        detect_video(YOLO(**vars(FLAGS)), FLAGS.input, FLAGS.output)
    else:
        print("Must specify at least video_input_path.  See usage with --help.")
