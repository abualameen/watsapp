#!/bin/bash
set -e

until pg_isready -h crm_db -p 5432 -U crm_user; do
  echo "Esperando a PostgreSQL..."
  sleep 2
done

exec "$@"
