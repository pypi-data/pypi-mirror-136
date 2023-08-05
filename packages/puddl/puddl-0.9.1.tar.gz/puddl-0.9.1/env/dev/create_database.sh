#!/bin/bash
set -euo pipefail

source .env

# generate initialization for postgres
# https://hub.docker.com/_/postgres/
cat <<EOF > env/dev/docker-entrypoint-initdb.d/000-create-db-and-user.sql
CREATE USER $PGUSER WITH CREATEROLE PASSWORD '$PGPASSWORD';
CREATE DATABASE $PGDATABASE OWNER $PGUSER;
EOF

docker-compose up -d db
