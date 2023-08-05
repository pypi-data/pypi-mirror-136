#!/bin/bash
set -euo pipefail

VENV=puddl-e2e-pypi
pyenv uninstall -f $VENV
pyenv virtualenv 3.9.6 $VENV

pip=~/.pyenv/versions/$VENV/bin/pip
puddl=~/.pyenv/versions/$VENV/bin/puddl

$pip install -q -U pip wheel

set -x
$pip install --upgrade puddl
$puddl db health
