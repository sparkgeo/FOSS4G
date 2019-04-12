from botocore.vendored import requests
import json
import urllib.parse
from urllib.parse import urljoin
import os

print('Loading function')

api_url =  os.environ['api_url']

def respond(err, res=None):
    print('RETURNED TEXT: ', res["text"])
    print('RETURNED ATTACHMENTS: ', res['attachments'])

    permanency = ["in_channel", "emphemeral"]

    requests.post(
        res['response_url'],
        data='{{"text": "{}", "attachments": {}, "response_type": "{}"}}'.format(
            res["text"],
            json.dumps(res["attachments"]),
            permanency[1]
        ),
        headers= {
            'Content-Type': 'application/json',
        }
    )

    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }

def create_session():
    session = requests.Session()
    session.headers['Accept'] = 'application/json'
    session.headers['User-Agent'] = 'Slack (darren@sparkgeo.com)'
    return session


def make_request(endpoint):
    session = create_session()

    result = session.request(endpoint['method'], endpoint['url'])
    data = result.json()

    return data

def format_fields(field_dict):
    fields = []
    title = None

    for key, value in field_dict.items():
        if key == "id":
            title = value
        else:
            fields.append(
                {
                    "title": key,
                    "value": json.dumps(value),
                    "short": False
                }
            )
    return (fields, title)

def create_attachment(title=None, image_url=None, fields=None, footer=None):
   return {
        "title": title,
        "image_url": image_url,
        "fields": fields,
        "footer": footer
    }

def format_simple_attachments(payload):
    fields, title = format_fields(payload)
    attachments = [create_attachment(fields=fields)]

    return {"attachments": attachments}

def format_complex_attachments(payload, iterable):
    attachments = []
    for item in payload[iterable]:

        image_url = item.get('assets')
        if image_url:
            image_url = image_url['thumbnail']['href']

        fields, title = format_fields(item)

        attachments.append(create_attachment(title, image_url, fields, title))

    return {"attachments": attachments}

def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))

    print("BODY:", event['body'])

    operations = ['POST']

    endpoints = {
        "info": {
            "url": urljoin(api_url, "stac"),
            "method": "GET"
        },
        "search": {
            "url": urljoin(api_url, "stac/search"),
            "method": "POST",
            "iterable": "features"
        },
        "collections": {
            "url": urljoin(api_url, "collections"),
            "method": "GET",
            "iterable": "collections"
        }
    }

    operation = event['httpMethod']
    if operation in operations:
        body_dict = urllib.parse.parse_qs(event['body'])
        print(body_dict)

        endpoint_type = body_dict['text'][0]
        endpoint = endpoints[endpoint_type]

        payload = make_request(endpoint)

        if endpoint_type in ["search", "collections"]:
            iterable = endpoints[endpoint_type]["iterable"]
            payload = format_complex_attachments(payload, iterable)
        elif endpoint_type in ["info"]:
            payload = format_simple_attachments(payload)

        payload["text"] = "STAC Query Results:"
        payload['response_url'] = body_dict['response_url'][0]

        response = respond(None, payload)
        print('RESPONSE:', response)
        if response.get('statusCode') != '200':
            print('STATUS NOT 200')
            return response
        else:
            print('HTTP 200 OK')
            return {'statusCode': '200',
                'headers': {
                    'Content-Type': 'application/json',
                }
            }
    else:
        return respond(ValueError('Unsupported method "{}"'.format(operation)))