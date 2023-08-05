# A Config Management CLI Tool similar to dynaconf for python 2 and above
=============================================================================

#### The library provides a basic cli tool `config_py2` to initialize a config mechanism in the current directory
Once installed you can run the `--help` to see the list of commands and options supported.

Please note that although the validation is missing currently, it will be supported in future releases.

```
$ config_py2 --help

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
                    Format of environment variables will be `ENV_PREFIX_{}`. By default it is set to 'CONFIG'
```

#### Examples to get you started with the `init` command
```
# Initializes a config_manager.py and settings.toml with placeholders for various environments
$ config_py2 init
Configuring your environment. Please Wait !


# Initializes a config_manager.py and settings.json with placeholders for various environments
$ config_py2 init -t json
Configuring your environment. Please Wait !


# Initializes a config_manager.py and settings.toml, settings-override.toml with placeholders for various environments
# Note that the configs will be read in the same order as provided during the `init` command
$ config_py2 init -f settings.toml -f settings-override.toml
Configuring your environment. Please Wait !


# This wil print the list of all configs as it'll be available for your application
$ config_py2 list
{
    "APP_ENV": "local",
    "CONFIG_ENVIRONMENT": "local"
}
```

#### Examples for usage in code once the config mechanism is initialized via the cli-tool
```
$ export CONFIG_ENVIROMENT=local

$ python
    >>> from config import settings
    >>> settings.APP_ENV
    'local'
    >>> settings.CONFIG_ENVIRONMENT
    'local'
```
