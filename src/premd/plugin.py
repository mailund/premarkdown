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


class _Plugins:
    def __init__(self):
        self._collect_plugins()

    def _load_plugins(self):
        """Method to guarantee that we only instanciate a plugin class once."""
        
        from pkg_resources import iter_entry_points
        self._plugins = {
            entry_point.name : entry_point.load()()
            for entry_point in iter_entry_points(group = "premd.plugins")
        }
        
    def _collect_tag_plugins(self):
        self._tag_plugins = {}
        for name, plugin in self._plugins.items():
            if not isinstance(plugin, TagPlugin):
                continue
            try:
                for tag in plugin.supported_tags:
                    self._tag_plugins[tag] = plugin   
            except:
                self._tag_plugins[name] = plugin            

    def _collect_summary_plugins(self):
        self._summary_plugins = {
            name: plugin 
            for name, plugin in self._plugins.items()
            if isinstance(plugin, SummaryPlugin)
        }

    def _collect_observer_plugins(self):
        self._observer_plugins = {
            plugin 
            for plugin in self._plugins.values()
            if isinstance(plugin, ObserverPlugin)
        }

    def _collect_plugins(self):
        self._load_plugins()
        self._collect_tag_plugins()
        self._collect_observer_plugins()
        self._collect_summary_plugins()

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

plugins = _Plugins()