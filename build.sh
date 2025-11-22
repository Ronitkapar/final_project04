#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install system dependencies
apt-get update && apt-get install -y ffmpeg imagemagick

# Modify ImageMagick policy to allow text (often disabled by default)
sed -i 's/none/read,write/g' /etc/ImageMagick-6/policy.xml

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
