
import sys
import os.path
import colorama ; colorama.init()
from file_scanning import flatten

def main():
	# FIXME: handle exceptions
	for line in flatten(sys.argv[1]):
		print(line.rstrip())

main()