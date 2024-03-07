# Github repositories API
_________________
## Информация
Этот проект представляет собой API и парсер GitHub (запускаемый на функциях Яндекса).

## Как запустить
Клонируйте репозиторий с GitHub и перейдите в директорию проекта:
```
git clone https://github.com/klishchov-bohdan/gitrepo-api
cd ./gitrepo-api
```
Переименуйте файл .env.dist в .env и заполните переменные окружения (уже заполнены данными моей бесплатной тестовой БД на https://elephantsql.com/):
Создайте новую сеть Docker с помощью команды:
```
docker network create "my-net"
```
Теперь вы можете запустить приложение с помощью команды `make run` или `docker compose up --build app`, если у вас не установлен make.
После этого `docker сompose` создаст контейнер с приложением Python, а также установит все зависимости. Вы можете получить доступ к документации API по адресу http://localhost:8000/docs

Если вы хотите запустить тесты, заполните файл .env.test своими данными (или оставьте как есть).
Теперь вы можете запустить тесты с помощью команды `make run_tests` или `docker compose --env-file .env.test up --build gitrepo_db_test app_tests`

### Yandex functions
В этом проекте создан парсер GitHub, который вы можете добавить в свою службу функций облака Яндекса.
Для создания функции Яндекса вам следует создать сервисную учетную запись в облаке Яндекса и авторизоваться в ней с помощью `yandex cli`.
Теперь вы можете заменить параметры функции для создания в Makefile и запустить команду `make deploy_func`, или просто выполните следующие команды в вашем терминале:
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
В параметре `--environment` вам следует заполнить учетные данные подключения к вашей базе данных PostgreSQL (или оставить как есть).
Теперь создайте триггер с помощью команды `make deploy_trigger` или:
```
yc serverless trigger create timer \
  		--name github-scraper-timer \
  		--cron-expression '0 2 ? * * *' \
  		--invoke-function-id <function-id> \
  		--retry-attempts 1 \
  		--retry-interval 10s \
```
Измените параметр `--invoke-function-id` на идентификатор созданной функции. Вы также можете изменить выражение cron для изменения периода вызова функции.

## Другая информация
Столбцы `position_cur` и `position_prev` вычисляются с помощью триггера PostgreSQL, созданного запросами:
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

Триггер создается при запуске вашего API. Я делаю так, потому что при запуске миграций, alembic не может работать с триггерами, а пакет alembic_utils недостаточно гибок и плохо работает с разными версиями PostgreSQL.

Я создаю триггер для функции Яндекса, которая запускается один раз в день в 3 часа ночи (по московскому времени), когда сервер и база данных будут менее нагружены.
