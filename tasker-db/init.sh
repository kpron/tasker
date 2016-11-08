#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE USER tasker;
    CREATE DATABASE tasker;
    GRANT ALL PRIVILEGES ON DATABASE tasker TO tasker;
EOSQL