
from . import utils
import copy
import os.path
import io
from subprocess import Popen, PIPE


def _get_filetype_dict(target):
	target_split = target.rsplit(".", 1)
	if len(target_split) == 2:
		return target_split[1]
	else:
		return None

class NoCommandException(Exception):
	pass

class RunCommand:
		
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
			filetype_dict = copy.deepcopy(config.get(('filetypes', filetype), {}))
		target_dict = copy.deepcopy(config.get(('targets', target), {}))
		
		conf = root
		utils.merge_dicts(conf, filetype_dict)
		utils.merge_dicts(conf, target_dict)
		
		# if there is a shared dict, update accordingly
		if "shared" in config:
			# shared can override command but arguments are added
			shared = config["shared"]
			if "command" in shared:
				conf["command"] = shared["command"]
			if "arguments" in shared:
				conf["arguments"].extend(shared["arguments"])

		# if the arguments contain spaces we need to split them for subprocess
		args = []
		for arg in conf["arguments"]:
			args.extend(arg.split())
		conf["arguments"] = args

		# finally, add the output file
		conf["arguments"].extend(['-o', target])

		if conf["command"] is None:
			raise NoCommandException

		self._cmdline = [conf["command"]] + conf["arguments"]

	def __enter__(self):
		self._process = Popen(self._cmdline, stdin = PIPE)
		self._stdin = io.TextIOWrapper(self._process.stdin)
		return self

	def __exit__(self, *foo):
		self._stdin.close()
		self._process.wait()

	@property
	def stdin(self):
		return self._stdin
	

