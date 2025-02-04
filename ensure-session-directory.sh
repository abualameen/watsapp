#!/bin/bash

# Ensure the session directory is created and has the correct permissions
mkdir -p /home/appuser/app/session-data
chown -R appuser:appuser /home/appuser/app/session-data

# Check if the directory is owned by appuser
if [ "$(stat -c %U /home/appuser/app/session-data)" != "appuser" ]; then
  echo "Error: /home/appuser/app/session-data is not owned by appuser"
  exit 1
fi

# Start the application
exec "$@"