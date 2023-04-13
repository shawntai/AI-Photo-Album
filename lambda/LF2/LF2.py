import json
import os
import inflection

import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

# For OpenSearch
REGION = "us-east-1"
# TODO: dynamically get the host url from aws
HOST = "search-photos-h6kdzh5mvw5n65qyy5vjpfwv4q.us-east-1.es.amazonaws.com"
INDEX = "photos"

# For Lex Bot
client = boto3.client("lexv2-runtime")


def lambda_handler(event, context):
    # Step 1: Get Query String from Frontend API call
    print("Hello from LF2!")
    print("Received event2: " + json.dumps(event))
    query_string = event["queryStringParameters"]["q"]
    print("Received query string: " + query_string)

    # Step 2: Get labels
    labels = get_search_targets_from_Lex(query_string)
    print("Labels: ", labels)

    # Step 3: AND together the labels
    #results = None
    #if len(labels) != 0:
        #labels_query = " + ".join(labels)
        #print("Labels query: ", labels_query)
        #results = opensearch_photo(labels_query)
    
    # Step 3: search by each labels and AND the results
    # try to have 5+ results
    results = []
    backup = [] # pictures that only contain one label
    initial_take_for_each_label = 20
    if len(labels) != 0:
        for label in labels:
            temp_results = opensearch_photo(label, initial_take_for_each_label)
            results.extend(temp_results)
    #         if results == None:
    #             results = temp_results
    #         else:
    #             results = list(set(results) & set(temp_results))
    #             backup.extend(list(set(temp_results) - set(results)))
    # if len(results) < 5:
    #     results.extend(backup[:5-len(results)])

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
        },
        "body": json.dumps({"results": results}),
    }


def get_search_targets_from_Lex(query_string):
    response = client.recognize_text(
        botId="Q2GXWRHAP2",  # MODIFY HERE
        botAliasId="TSTALIASID",  # MODIFY HERE
        localeId="en_US",
        sessionId="testuser",
        text=query_string,
    )
    print("lex-response", response)

    labels = []
    slots = response["sessionState"]["intent"]["slots"]
    print("slots", slots)
    # check first slot 'SearchTarget' if resolvedValues exists
    # since user may use CUSTOM_LABEL to search, we may use other than resolvedValues
    if (
        slots["SearchTarget"] != None
        and "resolvedValues" in slots["SearchTarget"]["value"]
        and (len(slots["SearchTarget"]["value"]["resolvedValues"]) > 0)
    ):
        labels.append(inflection.singularize(slots["SearchTarget"]["value"]["resolvedValues"][0]))
    if (
        slots["SearchTarget2"] != None
        and "resolvedValues" in slots["SearchTarget2"]["value"]
        and (len(slots["SearchTarget2"]["value"]["resolvedValues"]) > 0)
    ):
        labels.append(inflection.singularize(slots["SearchTarget2"]["value"]["resolvedValues"][0]))
    return labels


def opensearch_photo(labels, take=5):
    results = query(labels, take)
    img_paths = []
    for result in results:
        print(result["objectKey"])
        bucket = result["bucket"]
        key = result["objectKey"]
        if key not in img_paths:
            img_paths.append("https://" + bucket + ".s3.amazonaws.com/" + key)
    return img_paths


def query(term, take=5):
    q = {"size": take, "query": {"multi_match": {"query": term}}}

    client = OpenSearch(
        hosts=[{"host": HOST, "port": 443}],
        http_auth=get_awsauth(REGION, "es"),
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
    )

    res = client.search(index=INDEX, body=q)
    print(res)

    hits = res["hits"]["hits"]
    results = []
    for hit in hits:
        results.append(hit["_source"])

    return results


def get_awsauth(region, service):
    cred = boto3.Session().get_credentials()
    return AWS4Auth(
        cred.access_key, cred.secret_key, region, service, session_token=cred.token
    )
