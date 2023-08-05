import os
import tomli

script_dir = os.path.dirname(__file__)
file_path = os.path.join(script_dir, '../pyproject.toml')

with open(file_path, 'rb') as file:
    __version__ = tomli.load(file)['tool']['poetry']['version']
