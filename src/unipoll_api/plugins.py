import plistlib
from .timer_plugin import TimerPlugin

supported_plugins = {
    "timer": TimerPlugin
}

enabled_plugins = [
    "timer"
]


plugins = {}

def init_plugins():
    for plugin in enabled_plugins:
        plugins[plugin] = supported_plugins[plugin]()


def get_plugin(name):
    return plugins.get(name, None)


def run_plugin(name):
    plugin = get_plugin(name)
    if plugin is None:
        print("Plugin not found")
        return
    plugin.run()


async def run_plugins(action):
    if len(plugins) == 0:
        return await action
    result = None
    for name, plugin  in plugins.items():
        print(f'Running plugin "{name}"')
        result = await plugin.run(action, input=result)
        print(f"\nPlugin result: {result}")
    return result
        