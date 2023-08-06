import os
import math
import json
from pathlib import Path

import zipfile

def get_max_dim(trained_size, target_size, image_shape):
    '''
    1.) determine the scaling factor based on the train cell size and image under prediction cell size
    2.) calculate the least size that is bigger than the input and dividable by 64 (finalSize)

    This size will be set up in the Mask R-CNN config as the max dim.
    If the user does not provide anything (targetObjSize = -1) then we use the default size for training (1024) defined in the Mask R-CNN config file.
    '''
    
    resizeFactor = (trained_size/target_size)
    resizedShape = (resizeFactor*image_shape[0], resizeFactor*image_shape[1])
    resizedMaxDim = max(resizedShape)
    computed_size = int(math.ceil(resizedMaxDim/64)*64)
    return computed_size

def get_max_dim_pow2(pPredictSize):
    maxdim = pPredictSize
    temp = maxdim / 2 ** 6
    if temp != int(temp):
        maxdim = (int(temp) + 1) * 2 ** 6

    return maxdim

def get_max_dim_legacy(trainedObjSize, targetObjSize, image_shape):
    '''
    Legacy image size computation.
    '''

    resizeTo = (float(trainedObjSize) / float(targetObjSize / 2.0)) * (float(image_shape[0] + image_shape[1]) / 2.0)
    finalSize = int(round(resizeTo / 64) * 64)
    return finalSize

def unzip(zip, target):
    with zipfile.ZipFile(zip,"r") as zip_ref:
        zip_ref.extractall(target)

class NucleaizerEnv:

    default_home_subdir = '.nucleaizer'

    def __init__(self, nucleaizer_home_path=None):
        if nucleaizer_home_path is None:
            if 'NUCLEAIZER_HOME' in os.environ:
                self.nucleaizer_home_path = Path(os.environ['NUCLEAIZER_HOME'])
            else:
                self.nucleaizer_home_path = NucleaizerEnv.get_default_nucleaizer_path()
        else:
            self.nucleaizer_home_path = nucleaizer_home_path

    @staticmethod
    def get_default_nucleaizer_path():
        return Path.home() / NucleaizerEnv.default_home_subdir

    def get_nucleaizer_home_path(self):
        return self.nucleaizer_home_path

    def init_nucleaizer_dir(self):
        if not self.nucleaizer_home_path.exists():
            self.nucleaizer_home_path.mkdir(parents=True)

def json_load(file):
    data = None
    with open(file) as fp:
        data = json.load(fp)

    return data

def json_save(file, data):
    with open(file, 'w') as fp:
        json.dump(data, fp, indent=4)
