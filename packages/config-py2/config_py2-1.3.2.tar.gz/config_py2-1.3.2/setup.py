from os.path import isfile
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()
    fh.close()

if isfile("requirements.txt"):
    requirementsFile = "requirements.txt"
else:
    requirementsFile = "config_py2.egg-info/requires.txt"

with open(requirementsFile, "r") as fh:
    requirements = fh.read()
    fh.close()

VERSION = '1.3.2'

setup(
    name="config_py2",
    version=VERSION,
    author = 'Chalukya',
    author_email = 'chalukya@gmail.com',
    license = 'MIT',
    description = 'A Config Management CLI Tool similar to dynaconf for python 2 and above',
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://gitlab.com/chalukyaj/config-manager-python2",
    project_urls = {
        "Bug Tracker": "https://gitlab.com/chalukyaj/config-manager-python2/issues"
    },
    keywords=["config", "cli", "toml", "json", "yaml", "python2", "python 2.x", "dynaconf"],
    install_requires=[requirements],
    packages=['config_py2'],
    python_requires='>=2.7',
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Documentation',
        'License :: OSI Approved :: MIT License',
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent",
    ],
    entry_points={"console_scripts": ["config_py2 = config_py2.config_entrypoint:entrypoint"]},
)
