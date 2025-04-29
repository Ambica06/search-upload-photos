#!/bin/bash

set -e  # Exit immediately if a command fails

echo "Lambda files changed. Updating Lambda functions..."

# Update first Lambda (index-photos)
echo "Updating Lambda function: index-photos..."
aws lambda update-function-code \
  --function-name index-photos \
  --zip-file fileb://lambdas/lambda-function.zip

# Update second Lambda (search-photos)
echo "Updating Lambda function: search-photos..."
aws lambda update-function-code \
  --function-name search-photos \
  --zip-file fileb://lambdas/lambda-function.zip

echo "Both Lambda functions updated successfully."
