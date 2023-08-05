import config_entrypoint
from loader import Loader, Settings


class ConfigPy2:
    settings = None

    def __init__(self, envvar_prefix='CONFIG', settings_files=['settings.toml'], settings_dir='', dontLoad=False):
        Loader.ENV_PREFIX = envvar_prefix
        Loader.SETTINGS_FILES = settings_files
        Loader.SETTINGS_DIR = settings_dir
        if not dontLoad:
            self.load()

    def __new__(cls):
        return super(ConfigPy2, cls).__new__(cls)

    def load(self):
        # if ConfigPy2.settings:
        #     return
        Loader.load()
        ConfigPy2.settings = Loader.settings
