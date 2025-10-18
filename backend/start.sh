#!/bin/bash
# Start Flask app with Gunicorn for Render deployment
gunicorn -w 4 -b 0.0.0.0:$PORT run:app
