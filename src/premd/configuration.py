"""
Code for handling configuration files
"""

import os
import yaml
import pkg_resources
import collections
import functools

GLOBAL_CONFIGS = [
	pkg_resources.resource_filename("premd", "config.yml"),
	os.path.join(os.path.expanduser("~"), ".premd.yml")
]

def _collect_config_files(root_file):
	root_dir = os.path.dirname(root_file)
	project_config = os.path.join(root_dir, ".premd.yml")
	return GLOBAL_CONFIGS + [project_config]

def _read_config_files(filenames):
	configs = []
	for filename in filenames:
		with open(filename, 'r') as config_file:
			config = yaml.load(config_file)
			configs.append(config)
	return configs

def _merge_dicts(to_dict, from_dict):
    for key, val in from_dict.items():
    	# if we have a dict in both to and from dict, merge them
        if (key in to_dict and isinstance(to_dict[key], dict) 
        	and isinstance(val, collections.Mapping)):
            _merge_dicts(to_dict[key], val)
        else:
        	# if we do not know the key already, or 
        	# if we override it with something that is not
        	# a dict, simply overwrite
            to_dict[key] = val

class Configurations:

	def _build_configuration_dict(self, root_file):
		config_files = filter(
			os.path.isfile, 
			_collect_config_files(root_file)
		)
		yaml_dicts = _read_config_files(config_files)
		self._config_dict = {}
		for yd in yaml_dicts:
			_merge_dicts(self._config_dict, yd)

	def __init__(self, root_file):
		self._build_configuration_dict(root_file)

	def __getitem__(self, item):
		return self._config_dict[item]


