
import sys
import os.path

# Enable colours on Windows
import colorama ; colorama.init()
from termcolor import colored

import flatten
import plugin
	
plugins = plugin.Plugins()
def main():
	# FIXME: don't always output, sometimes we only want to summarise
	for line in flatten.flatten(sys.argv[1]):
		print(line.rstrip())

	outfile = sys.stderr # FIXME
	for name, plugin in sorted(plugins.summary_plugins.items()):
		header = plugin.__class__.__doc__
		print(colored(header, attrs = ["bold"]), file = outfile)
		print(colored('=' * len(header), attrs = ["bold"]), file = outfile)


		plugin.summarize(outfile)
		print(file = outfile)

main()