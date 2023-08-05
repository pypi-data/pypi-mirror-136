# rpa_logger

[![CI](https://github.com/kangasta/rpa_logger/actions/workflows/ci.yml/badge.svg)](https://github.com/kangasta/rpa_logger/actions/workflows/ci.yml)
[![Docs](https://github.com/kangasta/rpa_logger/actions/workflows/docs.yml/badge.svg)](https://github.com/kangasta/rpa_logger/actions/workflows/docs.yml)
[![Release](https://github.com/kangasta/rpa_logger/actions/workflows/release.yml/badge.svg)](https://github.com/kangasta/rpa_logger/actions/workflows/release.yml)
[![Maintainability](https://api.codeclimate.com/v1/badges/67a5ccd0ad707447f0be/maintainability)](https://codeclimate.com/github/kangasta/rpa_logger/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/67a5ccd0ad707447f0be/test_coverage)](https://codeclimate.com/github/kangasta/rpa_logger/test_coverage)

A simple python package for logging robotic process automation (RPA) progress.

## Getting started

This package is available in PyPI as [rpa-logger](https://pypi.org/project/rpa-logger/). To install, run:

```bash
pip3 install rpa-logger
```

See [package documentation](https://kangasta.github.io/rpa_logger/) and `examples` directory for instructions on getting started with the package usage.

## Documentation

The documentation for `main` branch is available in [GitHub pages](https://kangasta.github.io/rpa_logger/). It is generated with [pdoc](https://github.com/pdoc3/pdoc):

```bash
pdoc --html --output-dir docs rpa_logger
```

## Testing

Check and automatically fix formatting with:

```bash
pycodestyle rpa_logger
autopep8 -aaar --in-place rpa_logger
```

Run static analysis with:

```bash
pylint -E --enable=invalid-name,unused-import,useless-object-inheritance rpa_logger
```

Run unit tests with command:

```bash
python3 -m unittest discover -s tst/
```

Get test coverage with commands:

```bash
coverage run --branch --source rpa_logger/ -m unittest discover -s tst/
coverage report -m
```
