"""
Defining plugin protocols
"""

import abc
import collections

class TagPlugin(abc.ABC):
	@abc.abstractmethod
	def handle_tag(self, file, lineno, content):
		pass

class SummaryPlugin(abc.ABC):
    @abc.abstractmethod
    def summarize(self, outfile):
        pass

class ObserverPlugin(abc.ABC):
    @abc.abstractmethod
    def observe_line(self, filename, lineno, line):
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

    def _collect_observer_plugins(self):
        self._observer_plugins = []
        plugin_classes = list(ObserverPlugin.__subclasses__()) + \
                         list(ObserverPlugin._abc_registry)
        for plugin_class in plugin_classes:
            observer = self._register_plugin_class(plugin_class)
            self._observer_plugins.append(observer)

    def _collect_plugins(self):
        self._plugins = {}
        self._collect_tag_plugins()
        self._collect_observer_plugins()
        self._collect_summary_plugins()

    def __init__(self):
    	self._collect_plugins()

    @property
    def plugins(self):
        return self._plugins
    
   
    @property
    def tag_plugins(self):
        return self._tag_plugins

    @property
    def observer_plugins(self):
        return self._observer_plugins
    

    @property
    def summary_plugins(self):
        return self._summary_plugins

# FIXME: move concrete plugins to seperate files id:5
#   
# ----
# <https://github.com/mailund/premarkdown/issues/4>
# Thomas Mailund
# mailund@birc.au.dk
from termcolor import colored
class fixme(TagPlugin, SummaryPlugin):
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

class wc(ObserverPlugin, SummaryPlugin):
    """Word count in document"""
    def __init__(self):
        self.files = collections.OrderedDict()

    def observe_line(self, filename, lineno, line):
        if filename not in self.files:
            self.files[filename] = 0
        self.files[filename] += len(line.split())# FIXME: better recognition of words id:7
                                                 #   
                                                 # ----
                                                 # <https://github.com/mailund/premarkdown/issues/5>
                                                 # Thomas Mailund
                                                 # mailund@birc.au.dk

    def summarize(self, outfile):
        for filename, count in self.files.items():
            # FIXME: better formatting id:9
            #   
            # ----
            # <https://github.com/mailund/premarkdown/issues/6>
            # Thomas Mailund
            # mailund@birc.au.dk
            print(filename, count, file = outfile)

