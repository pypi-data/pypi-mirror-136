#!/bin/bash
set -euo pipefail

pyenv virtualenv 3.8.2 puddl-test || true

pip=~/.pyenv/versions/puddl-test/bin/pip
$pip install .
$pip install ../parrot/

puddl=~/.pyenv/versions/puddl-test/bin/puddl
$puddl --version
