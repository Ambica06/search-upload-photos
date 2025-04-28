import json
import boto3
import urllib.parse
import requests
from requests_aws4auth import AWS4Auth
from requests.auth import HTTPBasicAuth
import os
from datetime import timezone

# AWS clients
s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')
region = os.environ['AWS_REGION']
credentials = boto3.Session().get_credentials()
auth = AWS4Auth(credentials.access_key, credentials.secret_key, region, 'es', session_token=credentials.token)


username = os.environ['USERNAME']
password = os.environ['PASSWORD']

# OpenSearch endpoint and index
OPENSEARCH_ENDPOINT = 'https://search-photos-sqfijsxenxump2dtaoaihapgya.us-west-2.es.amazonaws.com'
INDEX_NAME = 'photos'

def lambda_handler(event, context):
    # Step 1: Get bucket and object key from S3 PUT event
    record = event['Records'][0]['s3']
    bucket = record['bucket']['name']
    key = urllib.parse.unquote_plus(record['object']['key'])

    # Step 2: Detect labels using Rekognition
    rekognition_labels = []
    try:
        response = rekognition.detect_labels(
            Image={'S3Object': {'Bucket': bucket, 'Name': key}},
            MaxLabels=10,
            MinConfidence=75
        )
        rekognition_labels = [label['Name'] for label in response['Labels']]
    except Exception as e:
        print("Error with Rekognition:", e)

    # Step 3: Retrieve custom metadata labels from S3 headObject
    custom_labels = []
    try:
        head = s3.head_object(Bucket=bucket, Key=key)
        metadata = head.get('Metadata', {})
        custom_labels_str = metadata.get('customlabels')  # auto-lowercased
        if custom_labels_str:
            custom_labels = [label.strip() for label in custom_labels_str.split(',')]
    except Exception as e:
        print("Error getting S3 metadata:", e)

    # Step 4: Merge labels into one array
    all_labels = list(set(custom_labels + rekognition_labels))

    # Step 5: Normalize timestamp format to match: "2018-11-05T12:40:02"
    timestamp = None
    if 'LastModified' in head:
        timestamp = head['LastModified'].astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')

    # Step 6: Prepare the JSON document to index in OpenSearch
    doc = {
        "objectKey": key,
        "bucket": bucket,
        "createdTimestamp": timestamp,
        "labels": all_labels
    }

    # Step 7: Store in OpenSearch
    try:
        url = f"{OPENSEARCH_ENDPOINT}/{INDEX_NAME}/_doc"
        headers = {"Content-Type": "application/json"}
        print(url)
        response = requests.post(
                    url,
                    auth=HTTPBasicAuth(username, password),  # Basic Authentication
                    headers=headers,
                    data=json.dumps(doc)  # Convert doc to JSON string
                )
        print("OpenSearch response:", response.status_code, response.text)
    except Exception as e:
        print("Error indexing to OpenSearch:", e)
