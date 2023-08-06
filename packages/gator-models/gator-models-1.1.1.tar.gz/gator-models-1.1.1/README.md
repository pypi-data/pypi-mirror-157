# gator-models
MongoDB models for Gator API

## Package manager
Gator-models uses the [poetry](https://python-poetry.org/) package manager to manage its dependencies. To install the dependencies, run the following command:
```
poetry install
```
See the [poetry](https://python-poetry.org/) documentation for more information and
installation instructions.

## Tools

#### Linting the codebase
For detecting code quality and style issues, run
```
flake8
```
For checking compliance with Python docstring conventions, run
```
pydocstyle
```

**NOTE**: these tools will not fix any issues, but they can help you identify potential problems.


#### Formatting the codebase
For automatically formatting the codebase, run
```
autopep8 --in-place --recursive .
```
For more information on this command, see the [autopep8](https://pypi.python.org/pypi/autopep8) documentation.

For automatically sorting imports, run
```
isort .
```