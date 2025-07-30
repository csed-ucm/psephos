from functools import lru_cache, cache
import importlib, pkgutil
# from timer_plugin import TimerPlugin
from unipoll_api.config import get_settings
from unipoll_api.utils import colored_dbg
settings = get_settings()


SUPPORTED_PLUGINS = [
    "timer",
    "test_plugin"
]


class PluginManager:
    def __init__(self):
        colored_dbg.info("Plugin Manager init")
        self.plugins = self.load_plugins()
        self.enabled_plugins = []

    def load_plugins(self):
        return {
            name: self.add_plugin(name, importlib.import_module(name).Plugin())
            for finder, name, ispkg in pkgutil.iter_modules()
            if name in settings.plugins and name in SUPPORTED_PLUGINS
        }

    def add_plugin(self, name, plugin):
        colored_dbg.info(f'Adding plugin "{name}"')
        return plugin
    
    def get_plugin(self, name):
        return self.plugins.get(name, None)
    
    def run_plugin(self, name):
        plugin = self.get_plugin(name)
        if plugin is None:
            print("Plugin not found")
            return
        plugin.run()
    
    async def run_plugins(self, action):
        if len(self.plugins) == 0:
            # print(f'No plugins enabled for action "{action}"')
            return await action
        result = None
        for name, plugin  in self.plugins.items():
            print(f'Running plugin "{name}"')
            result = await plugin.run(action, input=result)
            print(f"\nPlugin result: {result}")
        return result


# plugin_manager = PluginManager()


@cache
def get_plugin_manager() -> PluginManager:
    return PluginManager()