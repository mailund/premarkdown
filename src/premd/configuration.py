"""
Code for handling configuration files
"""

import os
import yaml
import pkg_resources
import collections
import functools
from . import utils

GLOBAL_CONFIGS = [
	pkg_resources.resource_filename("premd", "config.yml"),
	os.path.join(os.path.expanduser("~"), ".premd.yml")
]

def _collect_config_files(root_file):
	root_dir = os.path.dirname(root_file)
	project_config = os.path.join(root_dir, "premd.yml")
	return GLOBAL_CONFIGS + [project_config]

def _read_config_files(filenames):
	# At the *very* least we want a shared dict with a command
	# and a list of arguments. Now, these *should* be set
	# in the global configuration file, but just in case
	# we explicit start with that dict
	configs = [
		{
			"command": None,
			"arguments": []
		}
	]
	for filename in filenames:
		with open(filename, 'r') as config_file:
			config = yaml.load(config_file)
			configs.append(config)
	return configs


class Configurations(collections.UserDict):

	def _build_configuration_dict(self, root_file):
		config_files = filter(
			os.path.isfile, 
			_collect_config_files(root_file)
		)
		yaml_dicts = _read_config_files(config_files)

		self.data = {}
		for yd in yaml_dicts:
			utils.merge_dicts(self.data, yd)

	def __init__(self, root_file):
		self._build_configuration_dict(root_file)

	def __getitem__(self, path):
		try:
			d = self.data
			if isinstance(path, tuple):
				for key in path:
					d = d[key]
				return d
			else:
				return d[path]
		except:
			raise KeyError
