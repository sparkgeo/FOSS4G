prep-code:
	zip -g slack-stac-lambda.zip slack-stac-lambda.py

update-lambda-code:
	make prep-code
	aws lambda update-function-code \
		--profile sparkgeo \
		--function-name slack-stac \
		--region us-east-1 \
		--zip-file fileb://slack-stac-lambda.zip

update-lambda-config:
	aws lambda update-function-configuration \
		--profile sparkgeo \
		--function-name slack-stac \
		--region us-east-1 \
		--handler slack-stac-lambda.lambda_handler \
		--description "Slack slash command to query a STAC catalog"