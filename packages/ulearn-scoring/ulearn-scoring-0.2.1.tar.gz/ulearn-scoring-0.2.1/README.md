# ulearn-scoring

[![PyPI](https://img.shields.io/pypi/v/ulearn-scoring.svg)](https://pypi.org/project/ulearn-scoring/)
[![Changelog](https://img.shields.io/github/v/release/daniel55411/ulearn-scoring?include_prereleases&label=changelog)](https://github.com/daniel55411/ulearn-scoring/releases)
[![Tests](https://github.com/daniel55411/ulearn-scoring/workflows/Test/badge.svg)](https://github.com/daniel55411/ulearn-scoring/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/daniel55411/ulearn-scoring/blob/master/LICENSE)

Scoring of statements in ulearn by weeks

## Installation

Install this tool using `pip`:

    $ pip install ulearn-scoring

## Usage

    ulearn-scoring -c path/to/config.yaml -o path/to/result.csv
    
Example of config file is located at `tests/resources/config.yaml`

## Development

To contribute to this tool, first checkout the code. Then create a new virtual environment:

    cd ulearn-scoring
    python -m venv venv
    source venv/bin/activate

Or if you are using `pipenv`:

    pipenv shell

Now install the dependencies and test dependencies:

    pip install -e '.[test]'

To run the tests:

    pytest
