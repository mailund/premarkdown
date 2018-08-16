
import sys
import os.path
import argparse

# Enable colours on Windows
import colorama ; colorama.init()
from termcolor import colored

import flatten
import plugin

plugins = plugin.Plugins()

def _report_error(msg):
	output_msg = colored("Error", "red", attrs = ["bold"]) + ": " +msg
	print(output_msg, file = sys.stderr)

def _error(msg):
	_report_error(msg)
	sys.exit(1)

def _collect_commands():
	commands = {}
	for name, value in globals().items():
		if callable(value) and name.endswith("_command"):
			command_name = name.rsplit("_command", 1)[0]
			commands[command_name] = value
	return commands

# FIXME make this something you can plug in id:1
#   
# ----
# <https://github.com/mailund/premarkdown/issues/3>
# Thomas Mailund
# mailund@birc.au.dk
class Scanner:
	def __init__(self, lines):
		self.lines = lines

	def __iter__(self):
		for line in self.lines:
			yield line

class PrintScanner(Scanner):
	def __init__(self, outfile, lines):
		super().__init__(lines)
		self.outfile = outfile

	def __iter__(self):
		for line in self.lines:
			print(line, file = self.outfile)
			yield line

def scan(scanner):
	for _ in scanner:
		pass

## Commands
def summarize_command(args):
	"""Collect summary statistics"""
	parser = argparse.ArgumentParser(
		usage = "%(prog)s summarize [-h] infile [outfile]",
		description = summarize_command.__doc__
	)
	parser.add_argument(
		'infile', type = str
	)
	parser.add_argument(
		'outfile', nargs='?', type=argparse.FileType('w'),
	    default=sys.stdout
	)
	parser.add_argument(
		'--info', nargs='*', default = sorted(plugins.summary_plugins),
		help = "summarizers to run [{}]".format(
			", ".join(plugins.summary_plugins)
		)
	)

	args = parser.parse_args(args)
	
	scanner = Scanner(flatten.flatten(args.infile))
	scan(scanner)

	#for name, pluging in sorted(plugins.summary_plugins.items()):
	for name in args.info:
		plugin = plugins.summary_plugins[name]
		header = plugin.__class__.__doc__
		print(colored(header, attrs = ["bold"]), file = args.outfile)
		print(colored('=' * len(header), attrs = ["bold"]), file = args.outfile)

		plugin.summarize(args.outfile)
		print(file = args.outfile)

def transform_command(args):
	"""Run Markdown document through scanner plugins and output the result."""
	parser = argparse.ArgumentParser(
		usage = "%(prog)s transform [-h] infile [outfile]",
		description = transform_command.__doc__
	)
	parser.add_argument('infile', type=str)
	parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'),
	                     default=sys.stdout)
	parser.add_argument(
		'--info', nargs='*', default = [],
		help = "summarizers to run after processing [{}]".format(
			", ".join(plugins.summary_plugins)
		)
	)

	args = parser.parse_args(args)
	
	scanner = PrintScanner(args.outfile, flatten.flatten(args.infile))
	scan(scanner)

	for name in args.info:
		plugin = plugins.summary_plugins[name]
		header = plugin.__class__.__doc__
		print(colored(header, attrs = ["bold"]), file = sys.stderr)
		print(colored('=' * len(header), attrs = ["bold"]), file = sys.stderr)

		plugin.summarize(sys.stderr)
		print(file = sys.stderr)

## Main app
def main():
	commands = _collect_commands()
	commands_doc = "commands:\n{commands}".format(
		commands = "\n".join(
			"  {name:10}:\t{doc}".format(name = name, doc = command.__doc__)
			for name, command in commands.items()
		)
	)

	parser = argparse.ArgumentParser(
		formatter_class=argparse.RawDescriptionHelpFormatter,
		description = "Process a Markdown document.",
		epilog = commands_doc
	)
	parser.add_argument(
		'command',
		 help = "Subcommand to run"
	)
	parser.add_argument(
		'args', nargs = "*", default = [], 
		help = "Arguments to subcommand"
	)
	
	
	args = parser.parse_args(sys.argv[1:2]) # only first two 
	if args.command not in commands:
		_report_error("Unknown subcommand: {}".format(args.command))
		parser.print_help()
		sys.exit(1)
	
	commands[args.command](sys.argv[2:])

	
# Run this in case the module is called as a program...
main()