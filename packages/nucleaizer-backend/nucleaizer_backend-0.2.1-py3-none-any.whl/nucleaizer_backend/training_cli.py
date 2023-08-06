import argparse
from pathlib import Path

from .training import NucleaizerTraining
from .training import NucleaizerTraining
from .common import NucleaizerEnv
from .model_accessors import ZenodoModelList

class NucleaizerTrainingCli:

    def __init__(self, config):
        self.nucleaizer_env = NucleaizerEnv(config.nucleaizer_home)
        self.nucleaizer_env.init_nucleaizer_dir()

        self.inputs_dir = Path(config.inputs)
        self.workflow_dir = Path(config.workflow)
        if not self.workflow_dir.exists():
            self.workflow_dir.mkdir(parents=True)

        self.trainer = NucleaizerTraining(
            inputs_dir=str(self.inputs_dir),
            workflow_dir=str(self.workflow_dir),
            nucleaizer_home_path=str(self.nucleaizer_env.get_nucleaizer_home_path()),
            train_config_path=config.config_path)

    def train(self, tasks):
        self.trainer.init()
        if 'presegment' in tasks:
            model_list = ZenodoModelList(Path(self.nucleaizer_env.get_nucleaizer_home_path()))
            models = model_list.get_models()
            selected_model = None
            print('Available models:')
            for m in models:
                print(' - %s' % m.model_meta['name'])
                if m.model_meta['id'] == 'mask_rcnn_presegmentation':
                    selected_model = m
            print('Selected model:', selected_model.model_meta['name'])
            
            from nucleaizer_backend.mrcnn_interface.predict import MaskRCNNSegmentation
            selected_model_path = selected_model.access_resource(selected_model.model_meta['model_filename'])
            nucleaizer_instance = MaskRCNNSegmentation.get_instance(selected_model_path, selected_model.model_meta)

            self.trainer.copy_input()
            self.trainer.presegment(nucleaizer_instance)
            self.trainer.measure_cells()
            self.trainer.setup_db()
        
        if 'clustering' in tasks:
            print('clustering...')
            self.trainer.clustering()
        
        if 'style' in tasks:
            self.trainer.create_style_train()
            self.trainer.style_transfer()

        if 'train' in tasks:
            self.trainer.create_mask_rcnn_train()
            self.trainer.crop_training_set()
            self.trainer.train_maskrcnn(self.nucleaizer_env.get_nucleaizer_home_path()/'training/mask_rcnn_coco.h5', use_style_augmentation=True)
            self.trainer.deploy_model()

def get_cli_config():
    parser = argparse.ArgumentParser()
    parser.add_argument('--nucleaizer_home', type=str, default=None, 
        help='The nucleaizer home directory. It will be $HOME/.nucleaizer if omitted or $NUCLEAIZER_HOME if set.')

    parser.add_argument('--inputs', type=str, required=True, 
            help='The dataset directory containing the train val and test subfolders.')

    parser.add_argument('--workflow', type=str, default='workflow', 
            help='The working directory for the training.')

    parser.add_argument('--config_path', type=str, default=None, 
        help='Overwite the nucleaizer config file used for training. If not specified, a default will be used (after downloaded into the nucleaizer home directory).')

    parser.add_argument('--run_parts', type=str, default='presegment,clustering,style,train', 
            help='Modify which parts of the pipeline to execute (default: all).')

    return parser.parse_args()

def main():
    cli_config = get_cli_config()
    cli = NucleaizerTrainingCli(cli_config)
    tasks = cli_config.run_parts.split(',')
    cli.train(tasks)

if __name__ == '__main__':
    main()