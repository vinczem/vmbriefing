#!/usr/bin/with-contenv sh

# V-Briefing Entrypoint
echo "**********************"
echo "Starting V-Briefing..."
cd /app
# Start Gunicorn with 1 worker (sufficient for this add-on) and bind to 5000
exec gunicorn --bind 0.0.0.0:5000 --workers 1 --timeout 120 main:app
