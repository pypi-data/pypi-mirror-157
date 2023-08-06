from pathlib import Path

import requests

from . import remote
from .common import json_load

class ModelList:
    def get_models():
        '''
        Should return the list of available models.
        '''
        pass

    def get_short_description():
        pass

    def get_long_description():
        pass

class LocalModelList(ModelList):
    def __init__(self, models_dir: Path):
        super(LocalModelList, self).__init__()
        self.models_dir = models_dir
        self.models_list = self.get_models_list_()
        self.selected_idx = None
        self.models = []

    def get_models_list_(self):
        js = json_load(self.models_dir/'profiles.json')
        return js['models']

    def get_models(self):
        #self.models = []
        #models = model_db.get_models(self.models_dir)['models']
        
        for model_meta in self.models_list:
            self.models.append(LocalModelAccessor(self.models_dir, model_meta))
        
        return self.models

    def get_model(self, idx):
        return self.models[idx]

    def get_short_description(self):
        return "Local filesystem models (%s)" % self.models_dir

    def get_long_description(self):
        return "These models are loaded from the local filesystem."

class ZenodoModelList(ModelList):
    def __init__(self, cache_dir, zenodo_record_id=6790845, callback=None):
        self.zenodo_record_id = zenodo_record_id
        self.cache_dir = cache_dir
        if not self.cache_dir.exists():
            self.cache_dir.mkdir(parents=True)
        self.resource_urls = {}
        self.resource_urls = self.get_resource_urls()
        self.models_list = self.get_models_list()
        self.models = []
        self.callback = callback

    def get_resource_urls(self):
        resp = requests.get("https://zenodo.org/api/records/%d" % self.zenodo_record_id)
        files = resp.json()['files']
        resource_urls = {}
        for f in files:
            name = f['key']
            url = f['links']['self']
            print('Indexing resource URL: %s -> %s' % (name, url))
            resource_urls[name] = url
        return resource_urls

    def get_models_list(self):
        resp = requests.get(self.resource_urls['profiles.json'])    
        models_json = resp.json()
        return models_json['models']

    def get_models(self):
        for model_meta in self.models_list:
            model = ZenodoModelAccessor(self.cache_dir, self.resource_urls, model_meta, self.callback)
            self.models.append(model)
        return self.models

    def get_model(self, idx):
        return self.models[idx]

    def get_short_description(self):
        return 'Cloud models (Zenodo: <a href="https://zenodo.org/record/%d">%d</a>).' % (self.zenodo_record_id, self.zenodo_record_id)

    def get_long_description(self):
        return "These models are downloaded from the Zenodo repository through the public REST API (https://zenodo.org/record/%d)" % self.zenodo_record_id

class LocalModelAccessor():
    def __init__(self, models_dir: Path, model_meta: dict):
        super(LocalModelAccessor, self).__init__()
        self.models_dir = models_dir
        self.model_meta = model_meta

    def get_meta(self):
        return self.model_meta

    def get_resource_path(self, resource):
        return self.models_dir / resource

    def access_resource(self, resource):
        return self.models_dir / resource

    @staticmethod
    def from_path(model_path):
        '''
        If a .json file is selected, then we assume that it contains the model meta.
        Otherwise, we asseume that a weight file is selected and we construct an ad-hoc
        meta with default parameters.
        '''
        if model_path.suffix == '.json':
            meta = json_load(model_path)
            if 'name' not in meta:
                meta['name'] = model_path.stem
            if 'description' not in meta:
                meta['description'] = str(model_path)
            if 'model_filename' not in meta:
                raise ValueError("Can't find the model weights filename (model_filename) field that is mandatory.")
            return LocalModelAccessor(model_path.parent, meta)
        else:
            model_meta = {
                'name': model_path.stem, 
                'description': str(model_path), 
                'model_filename': model_path.name,
            }
            return LocalModelAccessor(model_path.parent, model_meta)

class ZenodoModelAccessor():
    '''
    Downloads the model if needed and caches it to the cache folder.
    '''
    def __init__(self, cache_dir, resource_urls, model_meta, callback):
        self.cache_dir = cache_dir
        self.resource_urls = resource_urls
        self.model_meta = model_meta
        self.callback = callback

    def get_local_path(self, resource):
        return self.cache_dir / resource

    def get_meta(self):
        return self.model_meta

    def access_resource(self, resource):
        if resource not in self.resource_urls:
            return None
        local_path = self.get_local_path(resource)
        if not local_path.exists():
            url = self.resource_urls[resource]
            remote.download_file(url, local_path, self.callback)
        return local_path