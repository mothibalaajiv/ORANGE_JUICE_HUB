# Tangy Town - Deployment Guide

## Python Version Requirement
**IMPORTANT: This application requires Python 3.11.9**

### For Local Development:
```bash
# Use pyenv or similar to install Python 3.11.9
pyenv install 3.11.9
pyenv local 3.11.9

# Or use conda
conda create -n tangytown python=3.11.9
conda activate tangytown
```

### For Production Deployment:
- **Heroku**: Uses `runtime.txt` (already configured)
- **Railway**: Uses `runtime.txt` (already configured)
- **DigitalOcean App Platform**: Specify Python 3.11.9 in app spec
- **AWS Elastic Beanstalk**: Use Python 3.11 platform
- **Docker**: Use `python:3.11.9` base image

## Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python run.py
```

## Environment Variables
Make sure to set these environment variables:
- `MONGODB_URI`
- `JWT_SECRET_KEY`
- `RAZORPAY_KEY_ID`
- `RAZORPAY_KEY_SECRET`
- `FRONTEND_URL`

## Notes
- All dependencies are pinned to specific versions for stability
- Only essential dependencies are included (no unused packages)
- Analytics features are disabled by default
- Background jobs use threading instead of APScheduler
- Geospatial operations use custom math calculations
