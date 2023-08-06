def _download_model():
    import urllib.request
    #model_url = 'https://github.com/etasnadi/Mask_RCNN/releases/download/v0.1-alpha/mask_rcnn_fluo_simple.h5'
    #urllib.request.urlretrieve(model_url, MODEL_NAME)
    return '/home/ervin/.nucleaizer/models/mask_rcnn_presegmentation.h5'

def _download_test_image():
    import imageio
    return imageio.imread('/home/ervin/nucleaizer_demo_folder/HoechstNuclearStain_Thermo.jpg')

def _test_prediction():    
    from nucleaizer_backend.mrcnn_interface.predict import MaskRCNNSegmentation
    model_path = _download_model()
    segmentation_instance = MaskRCNNSegmentation.get_instance(model_path)
    
    image = _download_test_image()
    result = segmentation_instance.segment(image)

def _test_empty_prediction():
    from nucleaizer_backend.mrcnn_interface.predict import MaskRCNNSegmentation
    model_path = _download_model()
    segmentation_instance = MaskRCNNSegmentation.get_instance(model_path)
    
    import numpy as np

    result = {
        'masks': np.zeros((256, 256, 0)),
        'scores': [],
        'class_ids': [],
    }
    
    '''
        boxes: [N, (y1, x1, y2, x2)] Bounding boxes in pixels       (N,4)
        class_ids: [N] Integer class IDs for each bounding box      (N,)
        scores: [N] Float probability scores of the class_id        (N,)
        masks: [height, width, num_instances] Instance masks        (H,W,N)
    '''

    results = [result]
    result = segmentation_instance.process_result(
        results, 
        image_shape=(256,256), 
        padding_ratio=0.0, 
        dilate=0.0, 
        cavity_fill=False, 
        pad_offsets=(0,0))