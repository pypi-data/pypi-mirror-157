import os
import os.path
import ast

import numpy as np
import cv2
import skimage.morphology
import tensorflow as tf
import imageio

from ..Mask_RCNN_tf2.mrcnn import utils
from ..Mask_RCNN_tf2.mrcnn import visualize
from ..Mask_RCNN_tf2.mrcnn import model

from .. import common
from . import nuclei_config
from . import kutils

class MaskRCNNSegmentation:

    '''
    An object that lazily creates a tensorflow session and then reuses for subsequent predictions.
    '''

    allowed_keys = [
        'model_path', 
        'detection_confidence',
        'detection_nms_threshold',
        'detection_max_instances',
        'default_image_size',
        'trained_object_size',
        'cavity_filling',  
        'dilation',
        'padding',
    ]

    @staticmethod
    def get_instance(model_path, model_meta={}):
        print('Loading nucleaizer model for prediction.')
        print('Weights path: %s' % model_path)
        print('Properties:')
        #kwargs = {k: ast.literal_eval(model_meta[k]) for k in MaskRCNNSegmentation.allowed_keys if k in model_meta}
        kwargs = {}
        for k in MaskRCNNSegmentation.allowed_keys:
            if k in model_meta:
                try:
                    kwargs[k] = ast.literal_eval(model_meta[k])
                    print('\t%s=%s' % (k, str(kwargs[k])))
                except ValueError:
                    print("Can't understand model parameter: %s=%s" % (k, model_meta[k]))
        
        return MaskRCNNSegmentation(model_path, **kwargs)

    def __init__(self, 
    model_path, 
    detection_confidence=0.5, 
    detection_nms_threshold = 0.35, 
    detection_max_instances=512, 
    default_image_size=2048,
    trained_object_size=40,
    cavity_filling=False,
    dilation=0,
    padding=0):

        self.model_path = model_path
        self.detection_confidence = detection_confidence
        self.detection_nms_threshold = detection_nms_threshold
        self.detection_max_instances = detection_max_instances
        self.default_image_size = default_image_size   # The default max dim
        self.trained_object_size = trained_object_size
        self.cavity_filling = cavity_filling
        self.dilation = dilation
        # Padding is disabled!
        #self.padding = padding
        self.padding = 0

        self.model = None                   # Stores the Mask R-CNN model
        self.last_max_dim = default_image_size
        self.session = None

        self.mask_rcnn_config = nuclei_config.NucleiConfig()
        self.mask_rcnn_config.DETECTION_MIN_CONFIDENCE = self.detection_confidence
        self.mask_rcnn_config.DETECTION_NMS_THRESHOLD = self.detection_nms_threshold
        self.mask_rcnn_config.DETECTION_MAX_INSTANCES=self.detection_max_instances
        self.mask_rcnn_config.IMAGE_MAX_DIM = self.last_max_dim
        self.mask_rcnn_config.IMAGE_MIN_DIM = self.last_max_dim
        self.mask_rcnn_config.__init__()

    @staticmethod
    def empty_result(height, width):
        return  \
            np.zeros((height, width), np.uint16), \
            np.zeros((height, width), np.uint16), \
            np.zeros((height, width, 0), np.uint8),\
            np.zeros(0, np.float)

    def segment(self, image, predict_size=None, target_size=None):

        '''
        @arg target_size: the expected size of the objects in the image. If given (-1), the ratio of the
        target_size and trained_size will be computed to determine the scaling (that will be passed to the Mask R-CNN in IMAGE_MAX_DIM parameter
        that in turn, resizes the image).
        @predict_size: if given, this scaling will be used for prediction and the trained size won't be considered.

        If both target_size and predict_size is given, an exception is raised.
        If none of them specified, then the default size will be used defined in the constructor.
        '''

        if target_size is not None and predict_size is not None:
            raise ValueError('Both target object size and predict size is defined.')

        if self.session is None:
            print('No session is saved, requesting the current Keras session and saving it...')
            gpus = tf.config.experimental.list_physical_devices('GPU')
            dev = gpus[0]
            print('Using device:', dev)
            tf.config.experimental.set_memory_growth(dev, True)
            
            self.session = tf.compat.v1.keras.backend.get_session()

        with self.session.as_default():
            with self.session.graph.as_default():
                # Rebuilding is needed when the Mask R-CNN config is changed.
                # or the model does not exist itself.
                print('Actual Keras session:', tf.compat.v1.keras.backend.get_session())
                rebuild = self.model is None

                image = kutils.RCNNConvertInputImage(image)

                extremes = (128, 2048)
                print('Computing max dim: target size: %s, trained size: %s' % (target_size, self.trained_object_size))
                computed_size = self.compute_max_dim(target_size, self.trained_object_size, predict_size, extremes, image.shape)
                print('Computed size: %s' % computed_size)

                if computed_size is not None and computed_size != self.last_max_dim:
                    print('Last max dim=%.2f is different than the current computed one=%.2f.' % (self.last_max_dim, computed_size))
                    print('Rebuilding the model...')
                    self.last_max_dim = computed_size
                    rebuild = True
                else:
                    print('Not updating the max dim!')

                print('Input image shape: %s; using max dim: %s' % (image.shape, self.last_max_dim))

                if rebuild:
                    print("Instatiating the Mak R-CNN model because it does not exist or config changed.")
                    print('Using image max dim:', self.last_max_dim)

                    self.mask_rcnn_config.IMAGE_MAX_DIM = self.last_max_dim
                    self.mask_rcnn_config.IMAGE_MIN_DIM = self.last_max_dim
                    self.mask_rcnn_config.__init__()

                    self.model = model.MaskRCNN(mode="inference", config=self.mask_rcnn_config, model_dir=os.path.dirname(self.model_path))
                    self.model.load_weights(self.model_path, by_name=True)

                pad_offsets = (0, 0)
                if self.padding > 0.0:
                    image, (offsetX, offsetY) = kutils.PadImageR(image, self.padding)
                    pad_offsets = (offsetY, offsetX)

                results = self.model.detect([image], verbose=0)

                return self.process_result(results, image.shape, self.padding, self.dilation, self.cavity_filling, pad_offsets)

    def compute_max_dim(self, target_size, trained_size, predict_size, extremes, image_shape):
        '''
        Target size: the median object size on the image given by the user.
        Trained size: the median object size the network trained on.
        Predict size: don't care the sizes, just rescale the images to the given size
        '''
        
        if target_size is not None:
            print('Target size is provided: %.2f; model trained size: %.2f' % (target_size, trained_size))
            computed_size = common.get_max_dim(trained_size, target_size, image_shape)
            computed_size = np.clip(computed_size, extremes[0], extremes[1])
        elif predict_size is not None:
            print('Predict size is provided: %.2f' % predict_size)
            computed_size = common.get_max_dim_pow2(predict_size)
        else:
            print('Neither target size nor predict size is provided. Using default size!')
            computed_size = None
        
        return computed_size

    def process_result(self, results, image_shape, padding_ratio, dilate, cavity_fill, pad_offsets):
            r = results[0]
            masks = r['masks']
            scores = r['scores']
            class_ids = r['class_ids']

            if masks.shape[:2] != image_shape[:2]:
                print("Invalid prediction.")
                return self.empty_result(image_shape[0], image_shape[1])

            count = masks.shape[2]
            if count < 1:
                print('No objects found in the image.')
                return self.empty_result(image_shape[0], image_shape[1])

            if padding_ratio > 0.0:
                masks = kutils.PadMask(image_shape, masks, pad_offsets)

            if dilate > 0:
                masks = kutils.DilateMask(masks, dilate)

            if cavity_fill and False:
                masks = kutils.CavityFill(masks)

            masks = kutils.SqueezeMask(masks)

            return kutils.MergeMasks(masks), masks, class_ids, scores

    def executeSegmentation(self, image, target_size):
        '''
        Called from Napari to segment an image.
        '''

        print('--> Segmenting image...')
        mask, masks, class_ids, scores = self.segment(image=image, target_size=target_size)

        count = masks.shape[2]
        print("Instances found: ", str(count))
        if count < 1:
            return None, None, None

        return mask, class_ids, scores