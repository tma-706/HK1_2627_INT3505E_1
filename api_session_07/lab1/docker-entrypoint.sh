#!/bin/sh

set -e

echo "Applying database migrations..."
flask --app wsgi:app db upgrade

echo "Starting API server..."
exec "$@"


