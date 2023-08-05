import tomli

with open('./pyproject.toml', 'rb') as file:
    __version__ = tomli.load(file)['tool']['poetry']['version']
