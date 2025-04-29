#!/bin/bash

set -e

echo "Updating both Lambda functions..."

# Update index-photos
echo "Updating index-photos Lambda..."
aws lambda update-function-code \
  --function-name index-photos \
  --zip-file fileb://index-photos.zip

# Update search-photos
echo "Updating search-photos Lambda..."
aws lambda update-function-code \
  --function-name search-photos \
  --zip-file fileb://search-photos.zip

echo "Both Lambda functions updated successfully!"
