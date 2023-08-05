# Javelin

CLI tool for managing Spearly deployments.

## Requirements
- `GITHUB_ACCESS_TOKEN` environment variable set to a **GitHub Personal Access Token** with `repo` scope ([Ref](https://github.com/settings/tokens))
- **AWS IAM User** with `codepipeline:StartPipelineExecution` permission to the required resources ([Ref](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#configuration))
- [**Poetry**](https://python-poetry.org)

## Installation
```sh
brew install pyenv
pyenv install

poetry install
or
pip install -r requirements.txt
```

## Usage
```sh
python -m javelin --help
```
