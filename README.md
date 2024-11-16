# investats

[![GitHub main workflow](https://img.shields.io/github/actions/workflow/status/dmotte/investats/main.yml?branch=main&logo=github&label=main&style=flat-square)](https://github.com/dmotte/investats/actions)
[![PyPI](https://img.shields.io/pypi/v/investats?logo=python&style=flat-square)](https://pypi.org/project/investats/)

:snake: **Inve**stment **stat**istic**s** calculator.

## Installation

This utility is available as a Python package on **PyPI**:

```bash
pip3 install investats
```

## Usage

There are some files in the [`example`](example) directory of this repo that can be useful to demonstrate how this tool works, so let's change directory first:

```bash
cd example/
```

We need a Python **virtual environment** ("venv") with some packages to do the demonstration:

```bash
python3 -mvenv venv
venv/bin/python3 -mpip install -r requirements.txt
```

TODO

For more details on how to use this command, you can also refer to its help message (`--help`).

## Development

If you want to contribute to this project, you can install the package in **editable** mode:

```bash
pip3 install -e . --user
```

This will just link the package to the original location, basically meaning any changes to the original package would reflect directly in your environment ([source](https://stackoverflow.com/a/35064498)).
