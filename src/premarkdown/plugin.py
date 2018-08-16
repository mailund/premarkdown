"""
Defining plugin protocols
"""

import abc
import collections

class TagPlugin(abc.ABC):
	@abc.abstractmethod
	def handle_tag(file, lineno, *rest):
		pass

class SummaryPlugin(abc.ABC):
    @abc.abstractmethod
    def summarize(outfile):
        pass    

class Plugins:
    __instance = None
    def __new__(cls): # make it a singleton
        if Plugins.__instance is None:
            Plugins.__instance = object.__new__(cls)
        return Plugins.__instance

    def _register_plugin_class(self, plugin_class):
        """Method to guarantee that we only instanciate a plugin class once."""
        if plugin_class not in  self._plugins:
            self._plugins[plugin_class] = plugin_class()
        return self._plugins[plugin_class]

    def _collect_tag_plugins(self):
        plugin_classes = list(TagPlugin.__subclasses__()) + \
                         list(TagPlugin._abc_registry)

        self._tag_plugins = {}
        for plugin_class in plugin_classes:
            plugin = self._register_plugin_class(plugin_class)
            try:
                for tag in plugin_class.supported_tags:
                    self._tag_plugins[tag] = plugin   
            except:
                self._tag_plugins[plugin.__class__.__name__] = plugin

    def _collect_summary_plugins(self):
        plugin_classes = list(SummaryPlugin.__subclasses__()) + \
                  list(SummaryPlugin._abc_registry)

        self._summary_plugins = {}
        for plugin_class in plugin_classes:
            plugin = self._register_plugin_class(plugin_class)
            self._summary_plugins[plugin.__class__.__name__] = plugin

    def _collect_plugins(self):
        self._plugins = {}
        self._collect_tag_plugins()
        self._collect_summary_plugins()

    def __init__(self):
    	self._collect_plugins()
   
    @property
    def tag_plugins(self):
        return self._tag_plugins

    @property
    def summary_plugins(self):
        return self._summary_plugins

# FIXME: mockup
from termcolor import colored
class FIXME(TagPlugin, SummaryPlugin):
    """FIXMEs in document."""
    supported_tags = [
        "FIXME", "Fixme", "fixme",
        "TODO", "Todo", "todo"
    ]

    def __init__(self):
        self.files = {}

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

