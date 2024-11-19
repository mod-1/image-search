import json
import boto3
import requests
import os
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize clients
lex = boto3.client('lexv2-runtime')

# Environment variables
elasticsearch_endpoint = os.environ['ELASTICSEARCH_ENDPOINT']
master_username = os.environ['MASTER_USERNAME']
master_password = os.environ['MASTER_PASSWORD']

def clean_data(query):
    word_list = query.split(" ")
    w_list = [word for word in word_list if word not in ["and", "or", ","]]
    return w_list

def get_labels(query):
    try:
        response = lex.recognize_text(
            botAliasId=os.environ['BOT_ALIAS_ID'],
            botId=os.environ['BOT_ID'],
            localeId='en_US',
            text=query
        )
        interpreted_value = response["interpretations"][0]["intent"]["slots"]["ObjectName"]["value"]["interpretedValue"]
        labels = clean_data(interpreted_value)
        return labels
    except Exception as e:
        logger.error(f"Error getting labels from Lex: {e}")
        return []

def get_photo_path(keys):
    try:
        index = 'data'
        url = f"{elasticsearch_endpoint}/{index}/_search"
        query = {
            "size": 100,
            "query": {
                "multi_match": {
                    "query": keys,
                }
            }
        }
        headers = {"Content-Type": "application/json"}
        r = requests.get(url, auth=(master_username, master_password),
                         headers=headers, data=json.dumps(query))
        response = r.json()
        
        image_list = [photo['_source']['objectKey'] for photo in response['hits']['hits']]
        return image_list
    except Exception as e:
        logger.error(f"Error getting photo path from OpenSearch: {e}")
        return []

def lambda_handler(event, context):
    try:
        query = event["queryStringParameters"]['q']
        label_list = get_labels(query)
        logger.info(f"Labels extracted: {label_list}")
        
        image_array = []
        for label in label_list:
            image_array.extend(get_photo_path(label))
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': '*',
                'Access-Control-Allow-Headers': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({"keys": image_array})
        }
    except Exception as e:
        logger.error(f"Error in lambda_handler: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': '*',
                'Access-Control-Allow-Headers': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({"error": "Internal Server Error"})
        }