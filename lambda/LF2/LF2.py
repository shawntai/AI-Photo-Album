import json
import os

import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

# For OpenSearch
REGION = 'us-east-1'
HOST = 'search-photos-h6kdzh5mvw5n65qyy5vjpfwv4q.us-east-1.es.amazonaws.com'
INDEX = 'photos'

# For Lex Bot
client = boto3.client('lexv2-runtime')

# write a function for hello world
def helloworld():
    print("Hello World")

def lambda_handler(event, context):
    # Step 1: Get Query String from Frontend API call
    print('Received event2: ' + json.dumps(event))
    query_string = event["queryStringParameters"]["q"]
    print("Received query string: "+query_string)
    
    # Step 2: Get labels
    labels = get_search_targets_from_Lex(query_string)
    print("Labels: ", labels)
    
    # Step 3: AND together the labels
    results = None
    if len(labels) != 0:
        labels_query = " + ".join(labels)
        print("Labels query: ", labels_query)
        results = opensearch_photo(labels_query)

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': '*',
        },
        'body': json.dumps({'results': results})
    }


def get_search_targets_from_Lex(query_string):
    response = client.recognize_text(
            botId='Q2GXWRHAP2', # MODIFY HERE
            botAliasId='TSTALIASID', # MODIFY HERE
            localeId='en_US',
            sessionId='testuser',
            text=query_string)
    print("lex-response", response)
    
    labels = []
    slots = response['sessionState']['intent']['slots']
    print("slots", slots)
    # check first slot 'SearchTarget' if resolvedValues exists
    if slots['SearchTarget'] != None and 'resolvedValues' in slots['SearchTarget']['value'] and (len(slots['SearchTarget']['value']['resolvedValues']) > 0):
        labels.append(slots['SearchTarget']['value']['resolvedValues'][0])
    if slots['SearchTarget2'] != None and 'resolvedValues' in slots['SearchTarget2']['value'] and (len(slots['SearchTarget2']['value']['resolvedValues']) > 0):
        labels.append(slots['SearchTarget2']['value']['resolvedValues'][0])
    if slots['SearchTarget3'] != None and 'resolvedValues' in slots['SearchTarget3']['value'] and (len(slots['SearchTarget3']['value']['resolvedValues']) > 0):
        labels.append(slots['SearchTarget3']['value']['resolvedValues'][0])
    return labels

def opensearch_photo(labels):
    results = query(labels)
    img_paths = []
    for result in results:
        print(result['objectKey'])
        bucket = result['bucket']
        key = result['objectKey']
        if key not in img_paths:
            img_paths.append('https://'+bucket+'.s3.amazonaws.com/'+key)
    return img_paths

def query(term):
    q = {'size': 5, 'query': {'multi_match': {'query': term}}}

    client = OpenSearch(hosts=[{
        'host': HOST,
        'port': 443
    }],
                        http_auth=get_awsauth(REGION, 'es'),
                        use_ssl=True,
                        verify_certs=True,
                        connection_class=RequestsHttpConnection)

    res = client.search(index=INDEX, body=q)
    print(res)

    hits = res['hits']['hits']
    results = []
    for hit in hits:
        results.append(hit['_source'])

    return results


def get_awsauth(region, service):
    cred = boto3.Session().get_credentials()
    return AWS4Auth(cred.access_key,
                    cred.secret_key,
                    region,
                    service,
                    session_token=cred.token)