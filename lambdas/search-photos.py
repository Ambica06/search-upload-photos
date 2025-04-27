import json
import boto3
import requests
from requests_aws4auth import AWS4Auth
import os
from requests.auth import HTTPBasicAuth

host = 'search-photos-sqfijsxenxump2dtaoaihapgya.us-west-2.es.amazonaws.com'
region = 'us-west-2'


username = os.environ['USERNAME']
password = os.environ['PASSWORD']

credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(
    credentials.access_key,
    credentials.secret_key,
    region,
    'es',
    session_token=credentials.token
)

def lambda_handler(event, context):
    # Handle preflight OPTIONS request
    if event['httpMethod'] == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
            },
            'body': json.dumps('OK')
        }

    # Fetch everything from OpenSearch index
    url = f"https://{host}/photos/_search"
    headers = { "Content-Type": "application/json" }
    body = {
        "size": 1000,  # get up to 1000 results, increase if needed
        "query": {
            "match_all": {}
        }
    }

    response = requests.get(url, auth=HTTPBasicAuth(username, password), headers=headers, data=json.dumps(body))

    print("DEBUG raw response:", response.text)

    res_json = response.json()

    search_results = []

    for hit in res_json.get('hits', {}).get('hits', []):
        print(hit)
        search_results.append(hit['_source'])

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
        },
        'body': json.dumps({'results': search_results})
    }
