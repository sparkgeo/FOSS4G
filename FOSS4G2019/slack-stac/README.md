# slack-stac

## Getting Started
1. Clone this repo
2. Create an AWS Lambda Function connected to API Gateway (can use Python microservices lambda function blueprint)
3. Run `make update-lambda-code` to deploy local lambda function code
4. Create an environment variable called `SLACKSTAC_API_URL` and set it to your STAC catalog api
5. Create a Slack slash command, and set the request URL to the API Gateway

## Syntax
Assuming your slash command is `/stac`, the following syntax is supported:
* `/stac info` returns metadata for the STAC
* `/stac collections` returns metadata for each collection
* `/stac search {query parameters}` where query parameters follow the syntax outlined in the [STAC API specification](https://github.com/radiantearth/stac-spec/blob/master/api-spec/api-spec.md). There must not be any spaces in the query parameters.
* Each command above supports the option to append a URL as the final argument, which overrides the `SLACKSTAC_API_URL` environment variable set in the lambda function

## Makefile
| Command              | Description                                                       
|----------------------|-------------------------------------------------------------------
| prep-code            | Zips lambda function code for deployment                             
| update-lambda-code   | Updates lambda function code on AWS                     
| update-lambda-config | Updates lambda function configuration on AWS
