import click
from os import environ
import toml, ujson, yaml
from os.path import isfile, join

class Settings:
    def __init__(self, env):
        self.CONFIG_ENVIRONMENT = env

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__

class Loader:
    settings = None
    ENV_PREFIX = 'CONFIG'
    SETTINGS_FILES = ['settings.toml']
    SETTINGS_DIR = ''

    @staticmethod
    def load():
        if not Loader.settings:
            Loader.settings = Settings('default')

        fileNames = Loader.SETTINGS_FILES

        envForConfig = environ.get('CONFIG_ENVIRONMENT')
        if not envForConfig:
            envForConfig = 'default'
        else:
            envForConfig = envForConfig.lower()

        Loader.settings.CONFIG_ENVIRONMENT = envForConfig

        defaultConfig = {}

        for fileName in fileNames:
            filetype = fileName.split('.')[-1]
            dumper = toml if filetype == 'toml' else (ujson if filetype == 'json' else yaml)

            fileName = join(Loader.SETTINGS_DIR, fileName)
            if isfile(fileName):
                with open(fileName, 'r') as f:
                    config = dumper.load(f) if filetype != 'yaml' else dumper.full_load(f)

                    defaultConfig.update(
                        config['default']
                    )

                    for key, value in defaultConfig.iteritems():

                        # Override Config
                        if envForConfig != 'default':
                            key = key.lower()

                            if key in config[envForConfig]:
                                value = config[envForConfig][key]
                            else:
                                key = key.upper()
                                if key in config[envForConfig]:
                                    value = config[envForConfig][key]

                        key = key.upper()
                        val = environ.get('{0}_{1}'.format(Loader.ENV_PREFIX, key))
                        if val:
                            value = val

                        setattr(Loader.settings, key, value)

                    f.close()
            else:
                click.echo("Config File {0} NOT found !!!".format(fileName))
                Loader.settings = None

        del defaultConfig
