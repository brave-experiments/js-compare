#!/usr/bin/env bash

pylint --rcfile pylintrc js_compare/ cli.py
mypy --config-file mypy.ini --strict js_compare/ cli.py
