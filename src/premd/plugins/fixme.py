
import collections
from .. import plugin

from termcolor import colored

class FIXME(plugin.TagPlugin, plugin.SummaryPlugin):
    """FIXMEs in document"""
    supported_tags = [
        "FIXME", "Fixme", "fixme",
        "TODO", "Todo", "todo"
    ]

    def __init__(self):
        self.files = collections.OrderedDict()

    def file_lines(self, filename):
        return self.files.setdefault(filename, collections.OrderedDict())

    def handle_tag(self, filename, lineno, tag, message):
        self.file_lines(filename)[lineno] = tag, message

    def summarize(self, outfile):
        for filename, lines in self.files.items():
            for lineno, (tag, message) in lines.items():
                    lineinfo = "{filename} ({lineno})".format(
                        filename = filename, lineno = lineno
                    )
                    print(
                        colored("▶", "red"),
                        colored("{:6}:".format(tag.upper()), attrs = ["bold"]),
                        colored(lineinfo, attrs = ["underline", "dark"]), ":",
                        message,
                        file = outfile
                    )
