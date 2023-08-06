import os
import sys
import platform
import subprocess

from . import remote
from . import common


# Option #1: call compiled MATLAB libraries
class MatlabNativeInterface():
    native_libraries = [
        'libfromClustersToStylesFunc', 
        'librunfromKaggleToClusters', 
        'libsetUpConfigAndDB', 
        'libSimpleScripts']

    def __init__(self, nucleaizer_home_path, outputs_dir):
        self.nucleaizer_home_path = nucleaizer_home_path
        self.download_library()
        self.set_matlab_rt_paths()
        self.set_native_paths(str(nucleaizer_home_path))
        os.environ['NUCLEAIZER_CONFIG'] = str(outputs_dir)
        os.environ['SAC_ROOT'] = str(nucleaizer_home_path/'sac')

    def download_library(self):
        download_file = self.nucleaizer_home_path / 'nucleaizer_matlab.zip'
        if not download_file.exists():
            remote.download_file(
                'https://github.com/etasnadi/nucleaizer_backend/releases/download/0.2.1/nucleaizer_matlab.zip',
                download_file)
            common.unzip(download_file, self.nucleaizer_home_path)

        download_file_sac = self.nucleaizer_home_path / 'sac.zip'
        if not download_file_sac.exists():
            remote.download_file(
                'https://github.com/etasnadi/nucleaizer_backend/releases/download/0.2.1/sac.zip',
                download_file_sac)
            common.unzip(download_file_sac, self.nucleaizer_home_path)

    def set_native_paths(self, nucleaizer_dir):
        print('Setting PYTHONPATH for the compiled libraries.')

        r = os.path.join(nucleaizer_dir, 'nucleaizer_matlab', '%s-%s' % (platform.system(), platform.processor()))
        p_ = ['%s/%s' % (str(r), x) for x in MatlabNativeInterface.native_libraries]
        os.environ['PYTHONPATH'] = ':'.join(p_)
        print('New PYTHONPATH=%s' % os.environ['PYTHONPATH'])

    def set_matlab_rt_paths(self):
        print('Checking MATLAB paths...')
        if 'MATLAB_RUNTIME_PATHS' in os.environ:
            matlab_rt = os.environ['MATLAB_RUNTIME_PATHS']
            path_list = '%s/v99/runtime/glnxa64:%s/v99/bin/glnxa64:%s/v99/sys/os/glnxa64:%s/v99/extern/bin/glnxa64' % (matlab_rt, matlab_rt, matlab_rt, matlab_rt)

            print('Configuring MATLAB Runtime path:', path_list)

            if 'LD_LIBRARY_PATH' in os.environ:
                os.environ['LD_LIBRARY_PATH'] += ':' + path_list
            else:
                os.environ['LD_LIBRARY_PATH'] = path_list
        else:
            print('The MATLAB Runtime paths assumed to be set before.')

    # These functions will be executed as subprocesses.
    def call_matlab_func(self, library_name, func_name, args):
        wrapper_args = [library_name, func_name] + args
        subprocess.run("%s -m nucleaizer_backend.matlab_func_wrapper %s" % (sys.executable, ' '.join(wrapper_args)), shell=True)

# Option #2: call matlab directly if installed.
class MatlabScriptInterface():
    def __init__(self, nucleaizer_home_path):
        matlab_command_var = 'MATLAB_COMMAND'
        if matlab_command_var in os.environ:
            self.matlab_command = os.environ[matlab_command_var]
        else:
            self.matlab_command = 'matlab'
        self.nucleaizer_home_path = nucleaizer_home_path
        self.repository_path = self.download_repository()

    def download_repository(self):
        dl_file = self.nucleaizer_home_path / 'biomagdsb.zip'
        extract_path = self.nucleaizer_home_path / 'biomagdsb'
        if not extract_path.exists():
            remote.download_file('https://api.github.com/repos/spreka/biomagdsb/zipball/master', dl_file)
            common.unzip(dl_file, extract_path)
        return list(extract_path.iterdir())[0]

    def run_matlab_command(self, command):
        cmd = '%s -nodisplay -nodesktop -nosplash -nojvm -r "%s"' % (self.matlab_command, command)
        cmd = cmd.replace('${PIPELINE_SCRIPTS}', os.path.join(self.repository_path, 'biomag-kaggle', 'src'))
        cmd = cmd.replace('${MATLAB_SCRIPTS}', os.path.join(self.repository_path, 'matlab_scripts'))
        subprocess.run(cmd, shell=True)

        return cmd