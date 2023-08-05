import click, toml, ujson, yaml
from loader import Loader, isfile, Settings


class Help(click.Command):
    def format_help(self, ctx, formatter):
        click.echo('''
Usage: config_py2 [OPTIONS] COMMAND [ARGS]

Options:
  --version         Show config_py2 version currently installed
  --help            Show this message and exit

Commands:
  init              Inits a config_py2 project. Default behavior of using `settings.toml` can be overriden with [ARGS]
  list              Lists all defined config values

Args:   Optionally use EITHER one of these in conjunction with `init` command
  -f, --filename    Pass one or more of this followed by a filename (with extension) to give a list of file(s) to use for config
  -t, --filetype    Pass one or more of this followed by a filetype (extension) to use for settings file.
                    Possible values are: [toml | json | yaml]
                    Please note that this option will not be used if filenames are passed via the -f, --filename flag
  -e, --env_prefix  Pass this option to override the ENV_PREFIX that will be used to override configs with the shell variables
                    Format of environment variables will be `ENV_PREFIX_{}`. By default it is set to \'CONFIG\''''
)


@click.command(cls=Help)
@click.argument('command', type=click.Choice(['init', 'list']))
@click.option('-f', '--filename', default='', multiple=True)
@click.option('-t', '--filetype', default='toml', type=click.Choice(['toml', 'json', 'yaml']))
@click.option('-e', '--env_prefix', default='CONFIG')
@click.version_option()
def entrypoint(command, filename, filetype, env_prefix):
    if command == 'init':
        init(filename, filetype, env_prefix)
    elif command == 'list':
        listConfig()

def init(fileNames, filetype, env_prefix):
    Loader.ENV_PREFIX = env_prefix
    if fileNames:
        Loader.SETTINGS_FILES = list(fileNames)
    else:
        fileNames = ['settings.{0}'.format(filetype)]
        Loader.SETTINGS_FILES = fileNames

    click.echo ("Configuring your environment. Please Wait !")

    for fileName in fileNames:
        if isfile(fileName):
            click.echo("File `{0}` already exists ! Exiting ...".format(fileName))
            exit(1)

        defaultConfig = {
            'default' : {},
            'local': {},
            'testing': {},
            'production': {}
        }
        with open(fileName, 'w') as f:
            dumper = None
            filetype = fileName.split('.')[-1]
            if filetype == 'toml':
                dumper = toml

            elif filetype == 'json':
                dumper = ujson

            elif filetype == 'yaml':
                dumper = yaml
                for key in defaultConfig.keys():
                    defaultConfig[key] = {'APP_ENV': key}

            if filetype != 'toml':
                dumper.dump(defaultConfig, f, indent=4)
            else:
                dumper.dump(defaultConfig, f)
        f.close()
    with open('config_manager.py', 'w') as f:
        f.write(
'''
from config_py2 import ConfigPy2
from os.path import dirname, realpath

settings = ConfigPy2(
    envvar_prefix   = '{0}' ,
    settings_files  = {1}   ,
    settings_dir    = dirname(realpath(__file__))
).settings
'''.format(env_prefix, fileNames)
        )
        f.close()

def listConfig():
    import sys
    from os import getcwd
    sys.path.insert(0, getcwd())
    from config_manager import settings

    click.echo(
        ujson.dumps(
            settings.values(),
            indent=4
        )
    )

if __name__ == '__main__':
    entrypoint()