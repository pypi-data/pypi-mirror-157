import os
import tomli

root_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
file_path = os.path.join(root_dir, 'pyproject.toml')

with open(file_path, 'rb') as file:
    __version__ = tomli.load(file)['tool']['poetry']['version']
