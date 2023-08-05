#!/bin/bash
set -euo pipefail

postgres_superuser_password=$(pwgen 20 2>/dev/null || echo "Eequepeidah5rae0ib8R")
db_password=$(pwgen 20 2>/dev/null || echo "aey1Ki4oaZohseWod2ri")

NAME=puddl
PORT=13370

cat <<EOF
COMPOSE_PROJECT_NAME=$NAME
HOST_UID=$(id -u)
HOST_GID=$(id -g)
POSTGRES_PASSWORD=$postgres_superuser_password
PGHOST=127.0.0.1
PGPORT=$PORT
PGDATABASE=$NAME
PGUSER=$NAME
PGPASSWORD=$db_password
EOF
