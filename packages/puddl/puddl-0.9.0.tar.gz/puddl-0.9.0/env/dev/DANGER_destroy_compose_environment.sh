#!/bin/bash
set -euo pipefail

# make sure that we are run from the project root
my_expected_name=./env/dev/DANGER_destroy_compose_environment.sh
my_actual_name=$0
if [[ "$my_expected_name" != "$my_actual_name" ]]; then
  echo "Please run me from the project root" >&2
  exit 1
fi

docker-compose down --remove-orphans
volumes=$(docker volume ls -q --filter label=puddl.dev)
[[ -n $volumes ]] && docker volume rm $volumes
