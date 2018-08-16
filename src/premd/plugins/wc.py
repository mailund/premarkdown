import collections
from .. import plugin

class WC(plugin.ObserverPlugin, plugin.SummaryPlugin):
    """Word count in document"""
    def __init__(self):
        self.files = collections.OrderedDict()

    def observe_line(self, filename, lineno, line):
        if filename not in self.files:
            self.files[filename] = 0

        # FIXME: better recognition of words id:7
        self.files[filename] += len(line.split())

    def summarize(self, outfile):
        for filename, count in self.files.items():
            # FIXME: better formatting id:9
            #   
            # ----
            # <https://github.com/mailund/premarkdown/issues/6>
            # Thomas Mailund
            # mailund@birc.au.dk
            print(filename, count, file = outfile)

