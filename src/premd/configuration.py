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

def _read_config_file(filename):
    try:
        with open(filename, 'r') as config_file:
            return yaml.load(config_file)
    except:
        return {}


class Configurations(collections.UserDict):


    def __init__(self):
        # At the *very* least we want a shared dict with a command
        # and a list of arguments. Now, these *should* be set
        # in the global configuration file, but just in case
        # we explicit start with that dict
        self.data = {
            "command": None,
            "arguments": []
        }
        for config_file in GLOBAL_CONFIGS:
            self._add_config_file(config_file)

    def _add_config_file(self, fname):
        yaml_dict = _read_config_file(fname)
        utils.merge_dicts(self.data, yaml_dict)

    def push_config(self, root_dir):
        project_config = os.path.join(root_dir, "premd.yml")
        self._add_config_file(project_config)

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
