def _get_constructor_args():
    from nucleaizer_backend.common import NucleaizerEnv
    env = NucleaizerEnv()
    env.init_nucleaizer_dir()

    nucleaizer_dir = str(env.get_nucleaizer_home_path())
    dataset_path = str(env.get_nucleaizer_home_path()/'dataset')
    project_dir = str(env.get_nucleaizer_home_path()/'workflow')

    return dataset_path, project_dir, nucleaizer_dir

def _set_matlab_paths():
    '''
    The native libraries are executed using the MATLAB Runtime v99.
    
    The user should install it first, then set the LD_LIBRARY_PATH correctly 
    (the exact paths printed out by the console installer).
    
    If the path did not set, the user can define the MATLAB_RUNTIME_PATHS var to point to the library where the
    MATLAB Runtime is installed then the script confgigures the LD_LIBRARY_PATH itself.
    '''
    import os
    os.environ['MATLAB_RUNTIME_PATHS'] = '/home/ervin/MATLAB/MATLAB_Runtime'
    #print('PYTHONPATH', os.environ['PYTHONPATH'])
    #print('LD_LIBRARY_PATH', os.environ['LD_LIBRARY_PATH'])

def _test_copy_input():
    '''
    Assumes that the $DATASET_DIR/test exists and contains the test images.
    Copies the contents into the $WORKFLOW_DIR/images.
    '''
    from nucleaizer_backend.training import NucleaizerTraining
    
    args = _get_constructor_args()
    _set_matlab_paths()
    trainer = NucleaizerTraining(*args)
    trainer.copy_input()

def _test_presegment():
    '''
    Assumes that the $WORKFLOW_DIR/images exists.
    Puts the results into the $WORKFLOW_DIR/presegment.
    '''
    from nucleaizer_backend.training import NucleaizerTraining
    
    args = _get_constructor_args()
    _set_matlab_paths()
    trainer = NucleaizerTraining(*args)

    from nucleaizer_backend.mrcnn_interface.predict import MaskRCNNSegmentation
    model_weights = '/home/ervin/.nucleaizer/models/mask_rcnn_presegmentation.h5'
    nucleaizer_instance = MaskRCNNSegmentation.get_instance(model_weights)

    trainer.presegment(nucleaizer_instance)

def _test_measure_cells():
    '''
    Assumes that the $WORKFLOW_DIR/presegment dir exists.
    Puts the results into $WORKFLOW_DIR/cellSizeEstimator.
    '''
    from nucleaizer_backend.training import NucleaizerTraining

    args = _get_constructor_args()
    _set_matlab_paths()
    trainer = NucleaizerTraining(*args)
    trainer.measure_cells()

def _test_setup_db():
    '''
    Needs the mask database ($NUCLEAIZER_DIR/clustering/masks) and 
    the distance learner ($NUCLEAIZER_DIR/clustering/pretrainedDistanceLearner.mat).
    Produces the $WORKFLOW_DIR/DB.mat and the $WORKFLOW_DIR/config.mat.
    '''
    from nucleaizer_backend.training import NucleaizerTraining

    args = _get_constructor_args()
    _set_matlab_paths()
    trainer = NucleaizerTraining(*args)
    trainer.setup_db()

def _test_clustering():
    '''
    Assumes that the $WORKFLOW_DIR/images and the $WORKFLOW_DIR/presegment exists.
    Puts the results into the $WORKLFOW_DIR/clusters.
    Needs the $WORKFLOW_DIR/config.mat.
    '''
    from nucleaizer_backend.training import NucleaizerTraining

    args = _get_constructor_args()
    _set_matlab_paths()
    trainer = NucleaizerTraining(*args)
    trainer.matlab_script = None
    trainer.clustering()

def _test_create_style_train():
    _set_matlab_paths()
    from nucleaizer_backend.training import NucleaizerTraining
    args = _get_constructor_args()
    _set_matlab_paths()
    trainer = NucleaizerTraining(*args)
    trainer.create_style_train()

def _test_style_transfer():
    _set_matlab_paths()
    from nucleaizer_backend.training import NucleaizerTraining
    args = _get_constructor_args()
    _set_matlab_paths()
    trainer = NucleaizerTraining(*args)
    trainer.style_transfer()

def _test_create_mask_rcnn_train():
    _set_matlab_paths()
    from nucleaizer_backend.training import NucleaizerTraining
    args = _get_constructor_args()
    trainer = NucleaizerTraining(*args)
    trainer.create_mask_rcnn_train()

def _test_matlab_interface():
    from nucleaizer_backend.training import MatlabInterface
    matlab = MatlabInterface('/home/ervin/devel/biomagdsb/biomag-kaggle/src')
    cmd = matlab.call_matlab_func('func', ['a', 'b'])
    print(cmd)

def _test_crop_image():
    _set_matlab_paths()
    from nucleaizer_backend.training import NucleaizerTraining
    args = _get_constructor_args()
    trainer = NucleaizerTraining(*args)
    import numpy as np
    im = np.zeros((6, 6, 3))
    cr = trainer.crop_image(im, target_size=(2, 2, 3))

def _test_crop_training_set():
    _set_matlab_paths()
    from nucleaizer_backend.training import NucleaizerTraining
    args = _get_constructor_args()
    trainer = NucleaizerTraining(*args)
    trainer.crop_training_set()

def _test_measure_cells_matlab():
    from nucleaizer_backend.training import NucleaizerTraining
    args = _get_constructor_args()
    trainer = NucleaizerTraining(*args)
    trainer.matlab_native = None
    trainer.measure_cells()

def _test_setup_db_matlab():
    from nucleaizer_backend.training import NucleaizerTraining
    args = _get_constructor_args()
    trainer = NucleaizerTraining(*args)
    trainer.matlab_native = None
    trainer.setup_db()

def _test_clustering_matlab():
    from nucleaizer_backend.training import NucleaizerTraining
    args = _get_constructor_args()
    trainer = NucleaizerTraining(*args)
    trainer.matlab_native = None
    trainer.clustering()

def _test_deploy_model():
    from nucleaizer_backend.training import NucleaizerTraining
    args = _get_constructor_args()
    trainer = NucleaizerTraining(*args)
    trainer.deploy_model()

def test_download_repository():
    from nucleaizer_backend.training import NucleaizerTraining
    args = _get_constructor_args()
    trainer = NucleaizerTraining(*args)
    trainer.download_training_assets()

def test_dummy():
    def always_true():
        return True
    
    assert always_true()==True