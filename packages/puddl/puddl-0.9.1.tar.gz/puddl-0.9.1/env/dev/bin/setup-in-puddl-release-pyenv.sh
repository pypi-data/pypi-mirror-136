#!/bin/bash
set -euo pipefail

pyenv virtualenv 3.8.2 puddl-latest || true

pip=~/.pyenv/versions/puddl-latest/bin/pip
puddl=~/.pyenv/versions/puddl-latest/bin/puddl

set -x
$pip install -U puddl
$puddl --version
