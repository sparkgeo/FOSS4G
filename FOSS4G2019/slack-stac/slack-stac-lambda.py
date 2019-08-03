from botocore.vendored import requests
import json
import urllib.parse
from urllib.parse import urljoin
import os

print('Loading function')

api_url =  os.environ.get('api_url')

def respond(err, res=None):
    print('RETURNED BLOCKS: ', res.get('blocks'))

    permanency = ["in_channel", "emphemeral"]

    requests.post(
        res['response_url'],
        data='{{"blocks": {}, "response_type": "{}"}}'.format(
            json.dumps(res.get("blocks")),
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


def make_request(endpoint, data=None):
    session = create_session()

    result = session.request(endpoint.get('method'), endpoint.get('url'), data=data)
    data = result.json()

    return data


def format_simple_block(payload):
    self_link = [i.get('href') for i in payload.get('links') if i.get('rel') == 'self'][0]

    return {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*<{self_link}|{payload.get('title')}>*\n{payload.get('description')}\nSTAC Version: {payload.get('stac_version')}"
                },
                "accessory": {
                    "type": "image",
                    "image_url": "http://sparkgeo.com/wp-content/uploads/2018/10/favicon-sparkgeo.png",
                    "alt_text": "Sparkgeo"
                }
            }
        ]
    }


def format_feature(payload):
    self_link = [i.get('href') for i in payload.get('links') if i.get('rel') == 'self'][0]

    assets = payload.get('assets')

    if assets:
        if assets.get('thumbnail'):
            image_url = assets.get('thumbnail').get('href')
        else:
            image_url = None
        downloads = ' | '.join([f"*<{v.get('href')}|{v.get('title')}>*" for k,v in assets.items()])

    return [
        {
            "type": "divider"
        }, {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"*<{self_link}|{payload.get('id')}>*\n"
                    f"*Timestamp*: {payload.get('properties').get('datetime')}\n"
                    f"*Collection*: {payload.get('properties').get('collection')}\n"
                    f"*Cloud Cover*: {payload.get('properties').get('eo:cloud_cover')}\n"
                    f"*Bounding Box*: {payload.get('bbox')}\n"
                    f"*Downloads*: {downloads}"
                )
            },
            "accessory": {
                "type": "image",
                "image_url": image_url,
                "alt_text": payload.get('id')
            }
        }
    ]


def format_collection(payload):
    self_link = [i.get('href') for i in payload.get('links') if i.get('rel') == 'self'][0]

    return [
        {
            "type": "divider"
        },{
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"*<{self_link}|{payload.get('title')}>*\n"
                    f"{payload.get('description')}\n"
                )
            },
            "accessory": {
                "type": "image",
                "image_url": "http://sparkgeo.com/wp-content/uploads/2018/10/favicon-sparkgeo.png",
                "alt_text": "Sparkgeo"
            }
        }
    ]


def format_complex_blocks(payload, iterable):
    found_count = payload.get('meta').get('found')
    returned_count = payload.get('meta').get('returned')
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"Found *{found_count}* {iterable}. Showing *{returned_count}* results."
            }
        }
    ]

    for item in payload.get(iterable):
        print('ITEM:', item)

        if iterable == 'collections':
            blocks += format_collection(item)
        elif iterable == 'features':
            blocks += format_feature(item)

    return {"blocks": blocks}


def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))

    print("BODY:", event.get('body'))

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

    operation = event.get('httpMethod')
    if operation in operations:
        body_dict = urllib.parse.parse_qs(event.get('body'))
        print(body_dict)

        body_text = body_dict.get('text')[0].split(' ')

        endpoint_type = body_text[0]
        endpoint = endpoints.get(endpoint_type)
        print('ENDPOINT:', endpoint)

        body_data = body_text[1].replace("'", '"') if len(body_text) > 1 else None
        print('BODY DATA:', body_data)

        payload = make_request(endpoint, body_data)
        print('PAYLOAD:', payload)

        if endpoint_type in ["search", "collections"]:
            iterable = endpoints.get(endpoint_type).get("iterable")
            payload = format_complex_blocks(payload, iterable)
        elif endpoint_type in ["info"]:
            payload = format_simple_block(payload)

        if body_data:
            payload['blocks'] += [
                {
                    "type": "divider"
                }, {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"Query: {body_data}"
                        }
                    ]
                }
            ]


        payload['response_url'] = body_dict.get('response_url')[0]

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