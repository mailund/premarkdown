"""running the premd script..."""

import sys
import os.path
import argparse

import colorama
from termcolor import colored

from . import configuration
from . import command
from . import flatten
from .plugin import plugins


# Enable colours on Windows
colorama.init()


# should always be set when we run a script!
CONFIGS = configuration.Configurations()


def _report_error(msg):
    output_msg = colored("Error", "red", attrs=["bold"]) + ": " + msg
    print(output_msg, file=sys.stderr)


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


def _get_input_file(args):
    if args.infile:
        root_dir = os.path.dirname(args.infile)
        CONFIGS.push_config(root_dir)
        infile = args.infile
    else:
        # if we do not have an infile then get it from configuration file
        root_dir = os.getcwd()
        CONFIGS.push_config(root_dir)
        try:
            infile = CONFIGS["root"]
        except KeyError:
            _error("""An input file should either be specified in the
configuration file or be provided on the commandline.""")

    if not os.path.isfile(infile):
        _error("No such file: {infile}".format(infile=infile))

    return infile


# FIXME make this something you can plug in id:1
#
# ----
# <https://github.com/mailund/premarkdown/issues/3>
# Thomas Mailund
# mailund@birc.au.dk

class Scanner:
    """Class for scanning through a file."""

    def __init__(self, lines):
        self.lines = lines

    def __iter__(self):
        for line in self.lines:
            yield line


class PrintScanner(Scanner):
    """Class for scanning through a file while printing 
to an output file
    """

    def __init__(self, outfile, lines):
        super().__init__(lines)
        self.outfile = outfile

    def __iter__(self):
        for line in self.lines:
            print(line, file=self.outfile)
            yield line


def scan(scanner):
    for _ in scanner:
        pass


def output_processed(infilename, outfile, run_plugins = True):
    scanner = PrintScanner(
        outfile,
        flatten.flatten(infilename, run_plugins)
    )
    scan(scanner)


def analyse_processed(infilename):
    scanner = Scanner(flatten.flatten(infilename))
    scan(scanner)


# Commands
# For formatting main argument parseing message
class MixedFormatter(argparse.ArgumentDefaultsHelpFormatter,
                     argparse.RawDescriptionHelpFormatter):
    pass


def summarize_command(args):
    """Collect summary statistics"""

    summarizer_doc = "summarizers:\n{commands}".format(
        commands="\n".join(
            "  {name:10}:\t{doc}".format(name=name, doc=command.__doc__)
            for name, command in plugins.summary_plugins.items()
        )
    )

    parser = argparse.ArgumentParser(
        formatter_class=MixedFormatter,
        usage="%(prog)s summarize [-h] infile [outfile]",
        description=summarize_command.__doc__,
        epilog=summarizer_doc
    )
    parser.add_argument(
        'infile', type=str, nargs='?'
    )
    parser.add_argument(
        'outfile', nargs='?', type=argparse.FileType('w'),
        default=sys.stdout
    )
    parser.add_argument(
        '--include', nargs='*',
        default=sorted(plugins.summary_plugins),
        help="summarizers to run",
        metavar='summarizer',
        choices=plugins.summary_plugins
    )

    args = parser.parse_args(args)
    infile = _get_input_file(args)
    
    analyse_processed(infile)

    for name in args.include:
        plugin = plugins.summary_plugins[name]
        header = plugin.__class__.__doc__
        print(colored(header, attrs=["bold"]), file=args.outfile)
        print(colored('=' * len(header), attrs=["bold"]), file=args.outfile)

        plugin.summarize(args.outfile)
        print(file=args.outfile)


def transform_command(args):
    """Process and output markdown file"""

    summarizer_doc = "summarizers:\n{commands}".format(
        commands="\n".join(
            "  {name:10}:\t{doc}".format(name=name, doc=command.__doc__)
            for name, command in plugins.summary_plugins.items()
        )
    )

    parser = argparse.ArgumentParser(
        formatter_class=MixedFormatter,
        usage="%(prog)s transform [-h] infile [outfile]",
        description=transform_command.__doc__,
        epilog=summarizer_doc
    )
    parser.add_argument(
        'infile', type=str, nargs='?'
    )
    parser.add_argument(
        'outfile', nargs='?', type=argparse.FileType('w'),
        default=sys.stdout
    )
    parser.add_argument(
        '--info', nargs='*', default=[],
        help="summarizers to run after processing",
        metavar='summarizer',
        choices=plugins.summary_plugins
    )

    args = parser.parse_args(args)
    infile = _get_input_file(args)
    output_processed(infile, args.outfile)

    for name in args.info:
        plugin = plugins.summary_plugins[name]
        header = plugin.__class__.__doc__
        print(colored(header, attrs=["bold"]), file=sys.stderr)
        print(colored('=' * len(header), attrs=["bold"]), file=sys.stderr)

        plugin.summarize(sys.stderr)
        print(file=sys.stderr)


def build_command(args):
    """Build an output file"""

    summarizer_doc = "summarizers:\n{commands}".format(
        commands="\n".join(
            "  {name:10}:\t{doc}".format(name=name, doc=command.__doc__)
            for name, command in plugins.summary_plugins.items()
        )
    )

    parser = argparse.ArgumentParser(
        formatter_class=MixedFormatter,
        usage="%(prog)s build [-h] [infile] [-o outfiles]",
        description=transform_command.__doc__,
        epilog=summarizer_doc
    )
    parser.add_argument(
        'infile', type=str, nargs="?"
    )
    parser.add_argument(
        "-o", "--targets",
        metavar="target",
        type=str, nargs="*"
    )
    parser.add_argument(
        '--info', nargs='*', default=[],
        help="summarizers to run after processing",
        metavar='summarizer',
        choices=plugins.summary_plugins
    )

    args = parser.parse_args(args)
    infile = _get_input_file(args)
    if args.info:
        info = args.info
    else:
        # if there are no info specified we get them from the configuration file
        try:
            info = CONFIGS["info"]
        except KeyError:
            info = []

    # Setup output file based on command line and configuration
    if args.targets is None:
        # Get targets from configurations
        try:
            targets = CONFIGS["targets"]
        except KeyError:
            _error("""Targets must be specified either in the configuration
file or on the commandline.""")
    else:
        targets = args.targets

    if not targets:
        _error("No targets specified.")

    run_plugins = True # used for only running plugins on first target
    for target in targets:
        try:
            open(target, "w")
        except IOError as ex:
            strerror = ex.args[1]
            _error("Couldn't open file {outfile}\n{ex}".format(
                outfile=target, ex=strerror
            ))

        with command.RunCommand(CONFIGS, target) as cmd:
            output_processed(infile, cmd.stdin, run_plugins)

        run_plugins = False # don't run the plugins for remaining targets

    for name in info:
        plugin = plugins.summary_plugins[name]
        header = plugin.__class__.__doc__
        print(colored(header, attrs=["bold"]), file=sys.stderr)
        print(colored('=' * len(header), attrs=["bold"]), file=sys.stderr)

        plugin.summarize(sys.stderr)
        print(file=sys.stderr)


# Main app
def main():
    "Main entry point for the script"
    commands = _collect_commands()
    commands_doc = "commands:\n{commands}".format(
        commands="\n".join(
            "  {name:10}:\t{doc}".format(name=name, doc=command.__doc__)
            for name, command in commands.items()
        )
    )

    parser = argparse.ArgumentParser(
        formatter_class=MixedFormatter,
        description="Process a Markdown document.",
        epilog=commands_doc
    )
    parser.add_argument(
        'command',
        help="Subcommand to run",
        metavar='command',
        choices=commands.keys()
    )
    parser.add_argument(
        'args', nargs="*",
        help="Arguments to subcommand"
    )

    args = parser.parse_args(sys.argv[1:2])  # only first two
    if args.command not in commands:
        _report_error("Unknown subcommand: {}".format(args.command))
        parser.print_help()
        sys.exit(1)

    commands[args.command](sys.argv[2:])


# Run this in case the module is called as a program...
if __name__ == "__main__":
    main()
