prep-code:
	zip -g slack-stac-lambda.zip slack-stac-lambda.py

update-lambda-code:
	make prep-code
	aws lambda update-function-code \
		--function-name slack-stac \
		--region us-east-1 \
		--zip-file fileb://slack-stac-lambda.zip

update-lambda-config:
	aws lambda update-function-configuration \
		--function-name slack-stac \
		--region us-east-1 \
		--handler slack-stac-lambda.lambda_handler \
		--description "Slack slash command to query a STAC catalog" \
		--environment '{"Variables":{"api_url":"${SLACKSTAC_API_URL}"}}'
