#!/bin/bash
echo "Starting Comment System..."

# Start Redis in background
redis-server --daemonize yes

# Start Django
daphne -b 0.0.0.0 -p 8000 comment_system.asgi:application