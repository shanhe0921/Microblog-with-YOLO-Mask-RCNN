import os
import sys
import warnings
warnings.filterwarnings('ignore',category=FutureWarning)
import random
import math
import numpy as np
import skimage.io
import matplotlib

import matplotlib.pyplot as plt

# Root directory of the project
ROOT_DIR = os.path.abspath("D:/yolo/Mask_RCNN-master")
# Uploaded image directory from web
PHOTOS_DIR = os.path.abspath('C:/Users/ZHENG/Desktop/microblog/upload')

# Import Mask RCNN
sys.path.append(ROOT_DIR)  # To find local version of the library
from mrcnn import utils
import mrcnn.model as modellib
from mrcnn import visualize
# Import COCO config
sys.path.append(os.path.join(ROOT_DIR, "samples/coco/"))  # To find local version
import coco
from keras.backend import clear_session
from keras import backend as K
if('tensorflow' == K.backend()):
    import tensorflow as tf
    import keras
    from keras.backend.tensorflow_backend import set_session

    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True
    config.gpu_options.per_process_gpu_memory_fraction = 0.6
    sess = tf.Session(config=config)
    K.set_session(sess)
    keras.backend.clear_session()
    

# Directory to save logs and trained model
MODEL_DIR = os.path.join(ROOT_DIR, "logs")

# Local path to trained weights file
COCO_MODEL_PATH = os.path.join(ROOT_DIR, "mask_rcnn_coco.h5")
# Download COCO trained weights from Releases if needed
if not os.path.exists(COCO_MODEL_PATH):
    utils.download_trained_weights(COCO_MODEL_PATH)

# Directory of images to run detection on
IMAGE_DIR = os.path.join(ROOT_DIR, "images")



# COCO Class names
# Index of the class in the list is its ID. For example, to get ID of
# the teddy bear class, use: class_names.index('teddy bear')
class_names = ['BG', 'person', 'bicycle', 'car', 'motorcycle', 'airplane',
               'bus', 'train', 'truck', 'boat', 'traffic light',
               'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird',
               'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear',
               'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie',
               'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
               'kite', 'baseball bat', 'baseball glove', 'skateboard',
               'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup',
               'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
               'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
               'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed',
               'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote',
               'keyboard', 'cell phone', 'microwave', 'oven', 'toaster',
               'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors',
               'teddy bear', 'hair drier', 'toothbrush']



class InferenceConfig(coco.CocoConfig):
    # Set batch size to 1 since we'll be running inference on
    # one image at a time. Batch size = GPU_COUNT * IMAGES_PER_GPU
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1

class MaskRCNN():
    def __init__(self):
        config = InferenceConfig()
        #config.display()

        # Create model object in inference mode.
        self._model = modellib.MaskRCNN(mode="inference", model_dir=MODEL_DIR, config=config)

        # Load weights trained on MS-COCO
        self._model.load_weights(COCO_MODEL_PATH, by_name=True)
        self._model.keras_model._make_predict_function()

    def detect_image(self, filedir, savedir, filename):
        # Load a image from the images folder
        image = skimage.io.imread(os.path.join(filedir, filename))
        # Run detection
        results = self._model.detect([image], verbose=1)
        # Visualize results
        r = results[0]
        visualize.save_image(image, filename, r['rois'], r['masks'],
        r['class_ids'],r['scores'],class_names,scores_thresh=0.9,save_dir=savedir,mode=0)
        return results
        

if __name__ == '__main__':
    rcnn = MaskRCNN()
    rcnn.detect_image('')