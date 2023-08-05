#!/bin/bash
set -euo pipefail

puddl index --source obs@f --dump \
  test/data/2019-11-01_18-26-42.mkv \
  > /tmp/puddl-test-dump.json
