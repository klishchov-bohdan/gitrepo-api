deploy_func:
	yc serverless function version create \
		--function-name=github-scraping \
		--runtime python311 \
		--entrypoint github_scraping.handler \
		--memory 1024m \
		--execution-timeout 600s \
		--source-path ./cloud_funcs/github-scraping.zip \
		--environment "username=oqnfoqos,password=O2e6FCvUsQ1fPC49UQIacBNSCsqUqgMc,host=cornelius.db.elephantsql.com,name=oqnfoqos"

deploy_trigger:
	yc serverless trigger create timer \
  		--name github-scraper-timer \
  		--cron-expression '0 2 ? * * *' \
  		--invoke-function-id d4eiq24gphnp1as7vtof \
  		--retry-attempts 1 \
  		--retry-interval 10s \

run:
	docker compose up --build app

run_tests:
	docker compose --env-file .env.test up --build gitrepo_db_test app_tests
