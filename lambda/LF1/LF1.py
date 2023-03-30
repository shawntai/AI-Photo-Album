import json
import boto3
from datetime import datetime
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth


def lambda_handler(event, context):
    print("LF1 triggered!")
    print(event)
    s3 = boto3.client("s3")
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = event["Records"][0]["s3"]["object"]["key"]
    rekognition = boto3.client("rekognition")
    rekognition_response = rekognition.detect_labels(
        Image={"S3Object": {"Bucket": bucket, "Name": key}}
    )
    detected_labels = [label["Name"] for label in rekognition_response["Labels"]]
    head_object = s3.head_object(Bucket=bucket, Key=key)
    custom_labels = []
    if "customlabels" in head_object["Metadata"]:
        custom_labels = head_object["Metadata"]["customlabels"].split(",")
    os_object = {
        "objectKey": key,
        "bucket": bucket,
        "createdTimestamp": datetime.now().strftime("%Y-%d-%mT%H:%M:%S"),
        "labels": detected_labels + custom_labels,
    }
    print(os_object)

    os_host = "search-photos-h6kdzh5mvw5n65qyy5vjpfwv4q.us-east-1.es.amazonaws.com"
    os_region = "us-east-1"
    os_service = "es"
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        os_region,
        os_service,
        session_token=credentials.token,
    )
    opensearch = OpenSearch(
        hosts=[{"host": os_host, "port": 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
    )
    opensearch.index(index="photos", body=os_object)

    return {"statusCode": 200, "body": json.dumps("Aloha from LF1!")}

    event = {
        "Records": [
            {
                "eventVersion": "2.1",
                "eventSource": "aws:s3",
                "awsRegion": "us-east-1",
                "eventTime": "2023-03-23T20:32:08.786Z",
                "eventName": "ObjectCreated:Put",
                "userIdentity": {
                    "principalId": "AWS:AROAYVJLLMDILSJ5AMIWK:BackplaneAssumeRoleSession"
                },
                "requestParameters": {"sourceIPAddress": "3.238.166.55"},
                "responseElements": {
                    "x-amz-request-id": "TMMZKPDSY9XA7ZKG",
                    "x-amz-id-2": "8PaEEf3tnpTnOYFkZ6JCG0gm2cG56hH0G4kZ7l6H/6YYcqs3OOfKFUiiCTKfLw2NF3fA95+FvW5Aqq4ieLfKnPJdNAEkv90v",
                },
                "s3": {
                    "s3SchemaVersion": "1.0",
                    "configurationId": "E1",
                    "bucket": {
                        "name": "cs6998-hw2-b2",
                        "ownerIdentity": {"principalId": "A11S6JH26YKIYF"},
                        "arn": "arn:aws:s3:::cs6998-hw2-b2",
                    },
                    "object": {
                        "key": "messi_7.jpg",
                        "size": 1136298,
                        "eTag": "3f060a3533a5e1431a1c904a4ad9d2c1",
                        "sequencer": "00641CB748A4EFAD13",
                    },
                },
            }
        ]
    }
