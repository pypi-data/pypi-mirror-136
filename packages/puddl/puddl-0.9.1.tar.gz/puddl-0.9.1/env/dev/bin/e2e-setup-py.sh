#!/bin/bash
set -euo pipefail

[[ -f setup.py ]]  # must be in root dir

VENV=puddl-e2e-setup-py
pyenv uninstall -f $VENV
pyenv virtualenv 3.9.6 $VENV

pip=~/.pyenv/versions/$VENV/bin/pip
puddl=~/.pyenv/versions/$VENV/bin/puddl

set -x
$pip install -e .
$puddl db health
