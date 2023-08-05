#!/bin/bash
set -euo pipefail

VENV=puddl-e2e-pypi
pip=~/.pyenv/versions/$VENV/bin/pip
puddl_db=~/.pyenv/versions/$VENV/bin/puddl-db

pyenv uninstall -f $VENV
pyenv virtualenv 3.9.6 $VENV

$pip install -q -U pip wheel

set -x
$pip install --upgrade puddl
$puddl_db health
