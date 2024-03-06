# Github repositories API
_________________
## Info
This project is an API and github scraper(running on yandex functions)

## How to run
Clone the repository from Github and go to project directory:
```
git clone https://github.com/klishchov-bohdan/gitrepo-api
cd ./gitrepo-api
```
Rename the file `.env.dist` to `.env` and fill in the environment variables (already filled with my free test db on https://elephantsql.com/):
Create a new Docker network using the command:
```
docker network create "my-net"
```
Now you can run application with `make run` command or `docker compose up --build app` if you have not `make` installed.
After which `docker сompose` will create three containers with a databases and a Python application and install all dependencies. You can access the API documentation by url address `http://localhost:8000/docs`

If you wanna run tests fill the `.env.test` file with your data (or you can leave as is)
Now, you can run tests with command `make run_tests` or `docker compose --env-file .env.test up --build gitrepo_db_test app_tests`

### Yandex functions
In this project created github scraper and you can add it to your yandex cloud functions service.
For creating yandex function you should create service account in yandex cloud and authorize in it using yandex cli.
Now, you can replace function parameters for creating in Makefile and run with command `make deploy_func`, or just run follows command in your terminal:
```
yc serverless function version create \
		--function-name=github-scraping \
		--runtime python311 \
		--entrypoint github_scraping.handler \
		--memory 1024m \
		--execution-timeout 600s \
		--source-path ./cloud_funcs/github-scraping.zip \
		--environment "username=oqnfoqos,password=O2e6FCvUsQ1fPC49UQIacBNSCsqUqgMc,host=cornelius.db.elephantsql.com,name=oqnfoqos"
```
In `--environment` parameter you should fill connection credentials for you postgres database (or just leave as is).
Now, create trigger with `make deploy_trigger` command or:
```
yc serverless trigger create timer \
  		--name github-scraper-timer \
  		--cron-expression '0 2 ? * * *' \
  		--invoke-function-id <function-id> \
  		--retry-attempts 1 \
  		--retry-interval 10s \
```
Change parameter `--invoke-function-id` on id of the created function. You also can change cron expression for changing function invoking period.

## Some information
Columns `position_cur` and `position_cur` calculating, using postgres trigger, created by queries:
```
CREATE OR REPLACE FUNCTION update_rating()
        RETURNS TRIGGER
        LANGUAGE PLPGSQL
        AS $$
        BEGIN
            UPDATE repository as main
            SET position_prev = position_cur, position_cur = subquery.rating
            FROM (SELECT id, RANK() OVER (ORDER BY stars DESC) AS rating
                FROM repository) as subquery
            WHERE main.id = subquery.id;
            RETURN NULL;
        END;

CREATE TRIGGER check_rating
        AFTER UPDATE OR INSERT OR DELETE
        ON repository
        FOR EACH ROW
        WHEN (pg_trigger_depth() < 1)
        EXECUTE PROCEDURE update_rating();
```

Trigger creates when you run your api. I make like this because when we run our migrations, alembic cant work with triggers and package `alembic_utils` not enough flexible and bad works with any Postgresql versions.

I create trigger for yandex function, which run it every day at 3am (Moscow time zone), when server and database are will be less loaded
