
import os.path
import contextlib

class CircularInclusionError(Exception):
	def __init__(self, filename, stack):
		msg = "Circular inclusion when importing {filename}.".format(
			filename = filename
		)
		super().__init__(msg)
		self.filename = filename
		self.stack = stack

@contextlib.contextmanager
def top_stack(stack, filename):
	if filename in stack:
		raise CircularInclusionError(filename, stack)
	stack.append(filename)
	yield stack
	stack.pop()

# FIXME: mockup
from termcolor import colored
def handle_FIXME(filename, lineno, message):
	lineinfo = "{filename:4}({lineno:3d})".format(
		filename = filename, lineno = lineno
	)
		
	print(
		"▶",
		#colored(lineinfo, attrs = ["underline", "dark"]),
		colored("FIXME", "red", attrs = ["bold"]) + ":",
		colored(message, attrs = ["underline"])
	)

def flatten(filename, stack = None):
	"""
	Recursively scan through files and yield all lines, 
	essentially pretending that the recursive sequence of files
	are a single sequence of lines.
	"""
	if stack is None:
		stack = []
	
	with top_stack(stack, filename) as stack, open(filename) as stream:
		for lineno, line in enumerate(stream):

			if line.startswith('%%'): # comments
				# See if we have a tag we can handle...
				tag, *rest = line[2:].split(':', maxsplit = 1)
				tag = tag.strip()
				rest = "" if rest == [] else rest[0].strip()

				# FIXME: mockup
				if tag == "FIXME":
					handle_FIXME(filename, lineno, rest)
				
				# Whether we handled a tag or not, we do not
				# yield a comment line.
				continue

			if line.startswith('//'): # A full path
				subfile_full = line[1:].strip()
				if os.path.isfile(subfile_full):
					yield from flatten(subfile_full, stack)
					continue

			if line.startswith('/'): # A relative path
				this_dir = os.path.dirname(filename)
				subfile = line[1:].strip()
				subfile_full = os.path.join(this_dir, subfile)
				if os.path.isfile(subfile_full):
					yield from flatten(subfile_full, stack)
					continue

			yield line.rstrip()
