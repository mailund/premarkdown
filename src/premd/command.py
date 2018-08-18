
from . import utils
import copy
import os.path
import subprocess

def _get_filetype_dict(target):
	target_split = target.rsplit(".", 1)
	if len(target_split) == 2:
		return target_split[1]
	else:
		return None

class NoCommandException(Exception):
	pass

class Command:
		
	def __init__(self, config, target):
		"""Class for building commandlines for building a target."""
		# build the conf from most general to most specific
		# we know that at least command and arguments will always be there
		root = { 
			"command": config["command"],
			"arguments": list(config["arguments"]) # make sure it is a copy
		}
		filetype = _get_filetype_dict(target)
		if filetype is None:
			filetype_dict = {}
		else:
			filetype_dict = copy.deepcopy(config.get(('filetype', filetype), {}))
		target_dict = copy.deepcopy(config.get(('targets', target), {}))
		
		self._conf = root
		utils.merge_dicts(self._conf, filetype_dict)
		utils.merge_dicts(self._conf, target_dict)
		
		# if there is a shared dict, update accordingly
		if "shared" in config:
			# shared can override command but arguments are added
			shared = config["shared"]
			if "command" in shared:
				self._conf["command"] = shared["command"]
			if "arguments" in shared:
				self._conf["arguments"].extend(shared["arguments"])

		# if the arguments contain spaces we need to split them for subprocess
		args = []
		for arg in self._conf["arguments"]:
			args.extend(arg.split())
		self._conf["arguments"] = args

		# finally, add the output file
		self._conf["arguments"].extend(['-o', target])

		if self._conf["command"] is None:
			raise NoCommandException

	def run(self, instream, outstream):
		cmdline = [self._conf["command"]] + self._conf["arguments"]
		subprocess.Popen(cmdline, stdin=instream)


