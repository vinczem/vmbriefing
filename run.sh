#!/usr/bin/with-contenv sh

# VMBriefing Entrypoint
echo "**********************"
echo "Starting VMBriefing..."
cd /app
# Start Gunicorn with 1 worker (sufficient for this add-on) and bind to 5000
exec gunicorn --bind 0.0.0.0:5000 --workers 1 --timeout 120 main:app
