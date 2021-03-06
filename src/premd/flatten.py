
import os.path
import contextlib
import re

from .plugin import plugins

FIGURE_RE = re.compile(r"!\[([^\]]*)\]\(([^\)]*)\)(.*)")

class CircularInclusionError(Exception):
	def __init__(self, filename, stack):
		msg = "Circular inclusion when importing {filename}.".format(
			filename = filename
		)
		super().__init__(msg)
		self.filename = filename
		self.stack = stack

@contextlib.contextmanager
def _add_to_stack(stack, filename):
	if filename in stack:
		raise CircularInclusionError(filename, stack)
	stack.append(filename)
	yield stack
	stack.pop()

def flatten(filename, run_plugins = True, stack = None):
	"""
	Recursively scan through files and yield all lines, 
	essentially pretending that the recursive sequence of files
	are a single sequence of lines.
	"""
	if stack is None:
		stack = []
	
	with _add_to_stack(stack, filename) as stack, open(filename) as stream:
		for lineno, line in enumerate(stream):
			# always get rid of trailing space (including newline)
			line = line.rstrip()

			if line.startswith('%%'): # comments
				# See if we have a tag we can handle...
				tag, *rest = line[2:].split(':', maxsplit = 1)
				tag = tag.strip()
				rest = "" if rest == [] else rest[0].strip()

				# Handle plugins
				if run_plugins and tag in plugins.tag_plugins:
					plugins.tag_plugins[tag].handle_tag(filename, lineno, tag, rest)
				
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

			if line.startswith('!['): # A figure
				match = FIGURE_RE.match(line)
				if match is not None:
					figlabel = match.group(1)
					figfile = match.group(2)
					trailing = match.group(3)
					if figfile.startswith('/'):
						# global path, do nothing
						pass
					else:
						# local filename, adjust to input file
						filedir = os.path.dirname(filename)
						figfile = os.path.join(filedir, figfile)
						line = "![{figlabel}]({figfile}){trailing}".format(
								figlabel=figlabel,
								figfile=figfile,
								trailing=trailing
						)						
				# do not continue, we want the figure text to be
				# included in the summaries

			if run_plugins:
				for observer in plugins.observer_plugins:
					observer.observe_line(filename, lineno, line)
				
			yield line
