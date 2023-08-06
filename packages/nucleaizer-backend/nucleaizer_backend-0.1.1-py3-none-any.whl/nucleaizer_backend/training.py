import os
import shutil
import pprint
import math
import random
import platform
from statistics import median
from pathlib import Path

import numpy as np
import imageio
from skimage.measure import regionprops
from skimage.transform import rescale

from .pix2pix_interface.style_transfer import StyleTransfer
from .mrcnn_interface.predict import MaskRCNNSegmentation
from .mrcnn_interface.train import MaskRCNNTrain
from .matlab_interfaces import MatlabScriptInterface, MatlabNativeInterface
from . import remote
from . import common
from .common import json_load, json_save

pp = pprint.PrettyPrinter(indent=4)

class NucleaizerTraining():

    def __init__(self, inputs_dir, workflow_dir, nucleaizer_home_path, train_config_path=None):
        '''

        The inputs go to the inputs_dir. Structure:
        inputs_dir/
            train/
                images/*.png
                masks/*.tiff
            val/
                images/*.png
                masks/*.tiff
            test/*.png

        The workflow_dir is the working directory for the training.

        The (downloaded) models, aux files, training work dir (by default) go into the nucleaizer_dir.

        '''

        '''
        Windows: script interface.
        Linux: choose native interface (can be overwritten by the user: USE_MATLAB_SCRIPT).
        The init method will lazily initialize these fields.
        '''
        self.matlab_script = None
        self.matlab_native = None


        self.inputs_dir = Path(inputs_dir)
        self.outputs_dir = Path(workflow_dir)

        self.nucleaizer_home_path = Path(nucleaizer_home_path)
        
        self.train_config_path = None
        if train_config_path is not None:
            self.train_config_path = Path(train_config_path)

        self.train_config = None

        self.style_learn_dir = self.outputs_dir/'styleLearnInput'
        self.split_ids = ['0', '1'] # Style transfer splits (in case of multiple train workers available)

        # Resize each image and mask pair to contain median cell sizes exaxtly this.
        self.train_cell_size = 40
        self.crop_size = (512, 512)

        if (self.inputs_dir/'clustering').exists():
            self.clustering_dir = self.inputs_dir/'clustering'
        else:
            self.clustering_dir = Path(nucleaizer_home_path)/'training/clustering'

        self.initialized = False

    def download_training_assets(self):
        download_file = self.nucleaizer_home_path / 'training.zip'
        if not download_file.exists():
            remote.download_file(
                'https://github.com/etasnadi/nucleaizer_backend/releases/download/0.2.1/training.zip',
                download_file)
            common.unzip(download_file, self.nucleaizer_home_path)

    def init_matlab_interface(self):
        use_script = False
        use_native = False

        if platform.system() == 'Windows':
            use_script = True
        elif platform.system() == 'Linux':
            if 'USE_MATLAB_SCRIPT' in os.environ:
                use_script = True
            else:
                use_native = True
        else:
            raise ValueError("Your system (%s) is not supported yet for training!" % platform.system())

        if use_script:
            self.matlab_script = MatlabScriptInterface(self.nucleaizer_home_path)
        if use_native:
            self.matlab_native = MatlabNativeInterface(self.nucleaizer_home_path, self.outputs_dir)

    def init(self):
        self.init_matlab_interface()
        self.download_training_assets()
        if self.train_config_path is not None:
            self.train_config = json_load(self.train_config_path)
        else:
            self.train_config = json_load(self.nucleaizer_home_path/'training/train.json')

        self.initialized = True

    def copy_input(self):
        # Copy test
        test_dir = self.inputs_dir/'test'
        
        workflow_input_images_dir = (self.outputs_dir/'images')
        print('Copying input files: %s -> %s' % (test_dir, workflow_input_images_dir))
        workflow_input_images_dir.mkdir(exist_ok=True, parents=True)

        for src_file in test_dir.glob('*.*'):
            shutil.copy(src_file, workflow_input_images_dir)

    def presegment(self, nucleaizer_instance):
        output_path = self.outputs_dir/'presegment'

        if not output_path.exists():
            output_path.mkdir(exist_ok=True, parents=True)

        predict_size=None
        input_path = self.outputs_dir/'images'

        for image_path in input_path.iterdir():
            print('Presegment:', image_path.name)
            if image_path.name.endswith('.png'):
                image = imageio.imread(image_path)
                mask, masks, class_ids, scores = nucleaizer_instance.segment(image, predict_size=predict_size)
                imageio.imwrite(output_path/('%s.tiff' % image_path.stem), mask)

    def measure_cells(self):
        args = [
            str(self.outputs_dir/'presegment') + '/', 
            str(self.outputs_dir/'cellSizeEstimator'/'images')]
        # Original matlab command to run:
        # matlab -nodisplay -nodesktop -nosplash -nojvm -r 
        # 
        # "addpath('${MATLAB_SCRIPTS}/cellSizeEstimateForPrediction');
        # cellSizeDataGenerate(
        #   '${OUTPUTS_DIR}/presegment/',
        #   '${CELLSIZE_EST}/images/');
        # exit;"
        if self.matlab_script is not None:
            self.matlab_script.run_matlab_command("addpath('${MATLAB_SCRIPTS}/cellSizeEstimateForPrediction'); cellSizeDataGenerate('%s','%s');exit;" % (args[0], args[1]))
        
        if self.matlab_native is not None:
            self.matlab_native.call_matlab_func('libSimpleScripts', 'cellSizeDataGenerate', args)

    def setup_db(self):
        args = [
            str(self.clustering_dir/'masks'),  # The mask database directory
            str(self.outputs_dir),                          # The database will be saved here
            str(self.clustering_dir/'pretrainedDistanceLearner.mat'), # The weights will be loaded from here
            '.'                                             # the codeBase dir, will be deprecated!
        ]
        # Original matlab command to run:
        # matlab -nodisplay -nodesktop -nosplash -nojvm -r 
        # 
        # "addpath('${PIPELINE_SCRIPTS}');
        # kaggleStartMatlab; 
        # setUpConfigAndDB(
        #   '${MASK_DB_DIR}',
        #   '${CLUSTER_CONFIG}',
        #   '${CLUSTER_CONFIG}/pretrainedDistanceLearner.mat',
        #   '${PIPELINE_SCRIPTS}'); 
        # exit;"

        if self.matlab_script is not None:
            self.matlab_script.run_matlab_command("addpath('${PIPELINE_SCRIPTS}');"
            "kaggleStartMatlab;setUpConfigAndDB('%s','%s','%s','${PIPELINE_SCRIPTS}');"
            "exit;" % (args[0], args[1], args[2]))

        if self.matlab_native is not None:
            self.matlab_native.call_matlab_func('libsetUpConfigAndDB', 'setUpConfigAndDB', args)

    def clustering(self):
        args = [
            str(self.outputs_dir/'images'),
            str(self.outputs_dir/'clusters'),
            'Kmeans-correlation-Best3Cluster', 
            str(self.outputs_dir/'presegment'),
            '/tmp', # placeholder
            '0', 'False'
        ]

        # Original matlab command to run:
        # matlab -nodisplay -nodesktop -nosplash -r 
        # 
        # "addpath('${PIPELINE_SCRIPTS}');
        # kaggleStartMatlab;
        # mergedImagesDir='${INPUT_IMAGES}';
        # clusterDir='${CLUSTER_DIR}';
        # sacFolder='${PIPELINE_SCRIPTS}/1_metalearning/matlab/sac/';
        # clusteringType ='Kmeans-correlation-Best3Cluster';
        # failCounter=0;
        # canContinue=false;
        # initialSegmentation='${PRESEGMENT}';
        # runfromKaggleToClusters(
        #   mergedImagesDir,
        #   clusterDir,
        #   clusteringType,
        #   initialSegmentation,
        #   sacFolder,
        #   failCounter,
        #   canContinue); 
        # exit;"
        if self.matlab_script is not None:
            self.matlab_script.run_matlab_command(
                "addpath('${PIPELINE_SCRIPTS}');"
                "kaggleStartMatlab;"
                "mergedImagesDir='%s';"
                "clusterDir='%s';"
                "sacFolder='${PIPELINE_SCRIPTS}/1_metalearning/matlab/sac/';"
                "clusteringType ='%s';"
                "failCounter=0;"
                "canContinue=false;"
                "initialSegmentation='%s';"
                "runfromKaggleToClusters(mergedImagesDir,clusterDir,clusteringType,initialSegmentation,sacFolder,failCounter,canContinue);exit;" % (args[0], args[1], args[2], args[3]))
        
        if self.matlab_native is not None:
            self.matlab_native.call_matlab_func('librunfromKaggleToClusters', 'runfromKaggleToClusters', args)

    def create_style_train(self):
        args = [
            str(self.style_learn_dir),
            str(self.outputs_dir/'clusters'),
            str(self.outputs_dir/'presegment'),
            str(self.clustering_dir/'basicOptions_02.csv'),
            str(self.style_learn_dir)
        ]

        # Original matlab command to run:
        # matlab -nodisplay -nodesktop -nosplash -nojvm -r 
        # 
        # "addpath('${PIPELINE_SCRIPTS}'); 
        # kaggleStartMatlab; 
        # styleTransTrainDir='${STYLE_INPUTS}'; 
        # clusterDir='${CLUSTER_DIR}';
        # initialSegmentation='${PRESEGMENT}'; 
        # splitOptionsFile='${CLUSTER_CONFIG}/basicOptions_02.csv'; 
        # artificialMaskDir='${SYNTHETIC_MASKS}'; 
        # fromClustersToStyles; 
        # exit;"
        if self.matlab_native is not None:
            self.matlab_native.call_matlab_func('libfromClustersToStylesFunc', 'fromClustersToStylesFunc', args)
        
        if self.matlab_script is not None:
            self.matlab_script.run_matlab_command(
                "addpath('${PIPELINE_SCRIPTS}'); "
                "kaggleStartMatlab;"
                "styleTransTrainDir='%s';"
                "clusterDir='%s';"
                "initialSegmentation='%s';"
                "splitOptionsFile='%s';"
                "artificialMaskDir='%s';"
                "fromClustersToStyles;"
                "exit;" % (args[0], args[1], args[2], args[3], args[4])
            )
    
    def collect_style_transfer_output(self, target_dir):
        im_list = Path(self.outputs_dir, self.style_learn_dir).glob('*/%s/images/*' % StyleTransfer.P2P_FINAl_OUTPUT_REL_DIR)
        mask_list = Path(self.outputs_dir, self.style_learn_dir).glob('*/%s/masks/*' % StyleTransfer.P2P_FINAl_OUTPUT_REL_DIR)

        target_img = target_dir/'images'
        target_mask = target_dir/'masks'

        target_img.mkdir(exist_ok=True, parents=True)
        target_mask.mkdir(exist_ok=True, parents=True)

        for im in im_list:
            shutil.copy(im, str(target_img))

        for im in mask_list:
            shutil.copy(im, str(target_mask))

    def style_transfer(self):
        for split in self.split_ids:
            split_dir = str(self.style_learn_dir / split)
            st = StyleTransfer(split_dir)
            st.learn_styles()
            st.apply_styles()
            st.generate_output()

        self.collect_style_transfer_output(self.outputs_dir/'augmentations'/'style')

    @staticmethod
    def get_median_ob_size(m):
        '''
        Checks all of the objects in the mask and computes the median size.
        '''
        props = regionprops(m)
        sizes = []
        for region in props:
            if region.label != 0: # Skip background
                bbox = region['bbox']
                h = bbox[2]-bbox[0]
                w = bbox[3]-bbox[1]
                sizes.append(.5*(h+w))
        median_size = median(sizes)
        return median_size

    @staticmethod
    def rescale_mask(mask, scale_factor):
        original_dtype = mask.dtype
        return rescale(mask, scale=scale_factor, order=0, anti_aliasing=False, preserve_range=True).astype(original_dtype)

    @staticmethod
    def rescale_image(image, scale_factor):
        original_dtype = image.dtype
        return rescale(image, scale=scale_factor, order=1, multichannel=True, anti_aliasing=True, preserve_range=True).astype(original_dtype)

    def enumerate_training_samples(self):
        '''
        Enumerates all of the samples in the initial Mask R-CNN training set 
        provided by the user and the synthetic images.
        '''

        from_train_maskrcnn = self.inputs_dir/'train'
        initial_images_list = list((from_train_maskrcnn/'images').glob('*.png'))
        initial_masks_list = list((from_train_maskrcnn/'masks').glob('*.tiff'))

        synthetic_images_list = list(self.style_learn_dir.glob('*/p2psynthetic/*/*.png'))
        synthetic_masks_list = list(self.style_learn_dir.glob('*/generated/*/grayscale/*.tiff'))

        # We don't really want to sort the files but to match them based on filenames 
        # or filenames+parent folders if they are equal.
        match_lambda = lambda posix_path: str(posix_path)[::-1]

        initial_images_list.sort(key=match_lambda)
        initial_masks_list.sort(key=match_lambda)

        synthetic_images_list.sort(key=match_lambda)
        synthetic_masks_list.sort(key=match_lambda)

        initial_samples = zip(initial_images_list, initial_masks_list)
        synthetic_samples = zip(synthetic_images_list, synthetic_masks_list)

        return list(initial_samples) + list(synthetic_samples)

    def create_mask_rcnn_train(self):
        '''
        1. Collectes all of the images that will be copied into the final training set,
        2. Resizes them to make the object sizes uniform through the dataset.
        3. Extract random crops from the images.
        '''

        mask_rcnn_training_dir = self.outputs_dir/'train_maskrcnn'

        (mask_rcnn_training_dir / 'images').mkdir(exist_ok=True, parents=True)
        (mask_rcnn_training_dir / 'masks').mkdir(exist_ok=True, parents=True)

        all_samples = self.enumerate_training_samples()
        for image_path, mask_path in all_samples:
            image = imageio.imread(str(image_path))
            mask = imageio.imread(str(mask_path))
            
            median_ob_size = self.get_median_ob_size(mask)
            scale_factor = self.train_cell_size / median_ob_size
            
            image_rescaled = self.rescale_image(image, scale_factor)
            mask_rescaled = self.rescale_mask(mask, scale_factor)

            print('name', image_path.stem, 'scale factor:', scale_factor, 'resize:', image.shape, '->', image_rescaled.shape)

            imageio.imwrite(mask_rcnn_training_dir/'images'/image_path.name, image_rescaled)
            imageio.imwrite(mask_rcnn_training_dir/'masks'/mask_path.name, mask_rescaled)

    def crop_image(self, im, mask, target_size=(512, 512, 3)):
        ry = random.randrange(0, max(im.shape[0]-target_size[0], 1))
        rx = random.randrange(0, max(im.shape[0]-target_size[0], 1))
        crop = im[ry:ry+target_size[0], rx:rx+target_size[1], ...]
        canvas = np.ones(target_size)*np.median(im)
        print('canvas, crop size',canvas.shape, crop.shape, 'crop coords', (ry, rx))


        cr_mask = np.zeros((target_size[0], target_size[1]), np.uint16)

        canvas[:crop.shape[0], :crop.shape[1], ...] = crop

        # Mask is always 2D
        cr_mask[:crop.shape[0], :crop.shape[1]] = mask[ry:ry+target_size[0], rx:rx+target_size[1], ...]

        return canvas, cr_mask

    def crop_training_set(self, crop_size=(512, 512)):
        '''
        Takes the training set with varying sized images ($WORKFLOW_DIR/train_maskrcnn)
        and extracts predefined sized crops from the images and the masks from random positions.
        The results are saved to ($WORKFLOW_DIR/train_maskrcnn_crops).
        If the image is smaller than the crop size, then the image will be padded with the median intensity.
        If the image is bigger thaan the crop size, then several number of crops will be extracted 
        proportionally to the ratio of the crop size and the image size.
        '''

        self.crop_size = crop_size

        mask_rcnn_training_dir = self.outputs_dir/'train_maskrcnn'
        mask_rcnn_crop_dir = self.outputs_dir/'train_maskrcnn_crops'
        
        (mask_rcnn_crop_dir/'images').mkdir(exist_ok=True, parents=True)
        (mask_rcnn_crop_dir/'masks').mkdir(exist_ok=True, parents=True)
        
        ims = sorted((mask_rcnn_training_dir/'images').iterdir())
        masks = sorted((mask_rcnn_training_dir/'masks').iterdir())

        for i_path,m_path in zip(ims, masks):
            print('Cropping:', i_path.name)

            i = imageio.imread(i_path)

            n_crops = max(math.ceil(np.prod(i.shape[:2]) / np.prod(crop_size)), 1)
            print('Extracting %s crops.' % n_crops)
            for cr_id in range(n_crops):
                if i.ndim == 3:
                    crop_dim = (crop_size[0], crop_size[1], i.shape[-1])
                else:
                    crop_dim = (crop_size[0], crop_size[1])
                m = imageio.imread(m_path)
                cr_i, cr_m = self.crop_image(i, m, crop_dim)
                imageio.imwrite(mask_rcnn_crop_dir/'images'/('%s_crop%d%s' % (i_path.stem, cr_id, i_path.suffix)), cr_i)
                imageio.imwrite(mask_rcnn_crop_dir/'masks'/('%s_crop%d%s' % (m_path.stem, cr_id, m_path.suffix)), cr_m)

    def train_maskrcnn(self, initial_model, use_style_augmentation=False):
        '''
        workflow/
            train_maskrcnn/
                images/
                masks/
            output_model/
                model.h5

        dataset/
            val/
                images/
                masks/
        '''

        if use_style_augmentation == True:
            mask_rcnn_training_dir = self.outputs_dir/'train_maskrcnn_crops'
        else:
            mask_rcnn_training_dir = self.inputs_dir/'train'
        
        trainer = MaskRCNNTrain(pParams=self.train_config["train_params"])
        output_model_path = self.outputs_dir/'output_model'
        output_model_path.mkdir(exist_ok=True)
        trainer.train(
            str(initial_model), 
            str(output_model_path/'model.h5'), 
            str(mask_rcnn_training_dir),
            str(self.inputs_dir/'val'))

    def deploy_model(self):
        '''
        Creates the config file to the model that can be loaded for prediction.
        '''

        meta = {
            'trained_object_size': self.train_cell_size,
            'description': 'Trained on: %s' % str(self.inputs_dir),
            'crop_size': str(self.crop_size)
        }

        (self.outputs_dir/'output_model').mkdir(exist_ok=True, parents=True)

        json_save(self.outputs_dir/'output_model'/'model.json', meta)