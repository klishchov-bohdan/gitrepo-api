import asyncio
import json
import os
from datetime import date
from typing import Final

import aiohttp
import requests
from bs4 import BeautifulSoup
from lxml import etree
from sqlalchemy import text, NullPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine


def parse_links():
    resp = requests.get('https://github.com/EvanLi/Github-Ranking/blob/master/Top100/Top-100-stars.md')
    bs = BeautifulSoup(resp.text, 'lxml')
    dom = etree.HTML(str(bs))
    links = dom.xpath('//article/table/tbody/tr/td[2]/a')
    hrefs = []
    for link in links:
        hrefs.append(link.get('href').replace('\\', '').replace('"', ''))
    return hrefs


def short_digit_to_int(short: str):
    if '.' in short:
        short = short.replace('.', '').replace('k', '00').replace('+', '')
    else:
        short = short.replace('k', '000').replace('+', '')

    return int(short)


async def parse_repo(url, retry: int):
    try:
        timeout = aiohttp.ClientTimeout(total=60)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as resp:
                bs = BeautifulSoup(await resp.text(), 'lxml')
        dom = etree.HTML(str(bs))
        repo_name = dom.xpath('//*[@id="repository-container-header"]/div[1]/div[1]/div/strong/a')[-1].text.strip()
        repo_owner = dom.xpath('//*[@id="repository-container-header"]/div[1]/div[1]/div/span[1]/a')[-1].text.strip()
        try:
            repo_stars = dom.xpath('//div[@class="mt-2"]/a/strong')[0].text.strip()
        except Exception as ex:
            repo_stars = '0'
        try:
            repo_watching = dom.xpath('//div[@class="mt-2"]/a/strong')[1].text.strip()
        except Exception as ex:
            repo_watching = '0'
        try:
            repo_forks = dom.xpath('//div[@class="mt-2"]/a/strong')[2].text.strip()
        except Exception as ex:
            repo_forks = '0'
        try:
            repo_issues = dom.xpath('//span[@id="issues-repo-tab-count"]')[-1].text.strip()
        except Exception as ex:
            repo_issues = '0'
        try:
            repo_language = dom.xpath('//ul[@class="list-style-none"]/li/a/span[@class="color-fg-default text-bold mr-1"]')[0].text.strip()
        except Exception as ex:
            repo_language = "None"
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(str(resp.url)+'/activity?time_period=year') as activity_resp:
                data = await activity_resp.read()
                resp_json = json.loads(data)
        activity_list = resp_json['payload']['activityList']['items']
        repo_activity = []
        for activity in activity_list:
            repo_activity.append({
                'pushed_at': activity['pushedAt'],
                'name': activity['pusher']['login']
            })
        print(repo_name)
        return {
            'repo': repo_name,
            'owner': repo_owner,
            'stars': short_digit_to_int(repo_stars),
            'watchers': short_digit_to_int(repo_watching),
            'forks': short_digit_to_int(repo_forks),
            'open_issues': short_digit_to_int(repo_issues),
            'language': repo_language,
            'activity': repo_activity
        }
    except Exception as ex:
        print(ex)
        if retry == 0:
            return {}
        else:
            await asyncio.sleep(3)
            return await parse_repo(url, retry - 1)


async def save_to_db(repos: list[dict], engine: AsyncEngine):
    authors = []
    commits = []
    for repo in repos:
        for commit in repo['activity']:
            author_name = {
                'name': commit['name']
            }
            if author_name not in authors:
                authors.append(author_name)
            commit_date = commit['pushed_at'].split('T')[0].split('-')
            new_commit = {
                'id': repo['repo'] + '_' + commit['name'] + '_' + commit['pushed_at'],
                'repo_name': repo['repo'],
                'author_name': commit['name'],
                'pushed_at': date(*[int(d) for d in commit_date])
            }
            if new_commit not in commits:
                commits.append(new_commit)
    repo_stmt = text(f'''
                INSERT INTO repository (repo, owner, stars, watchers, forks, open_issues, language) 
                VALUES (:repo, :owner, :stars, :watchers, :forks, :open_issues, :language)
                ON CONFLICT (repo) DO UPDATE 
                    SET stars = EXCLUDED.stars, watchers = EXCLUDED.watchers, forks = EXCLUDED.forks, open_issues = EXCLUDED.open_issues, language = EXCLUDED.language;
            ''')
    authors_stmt = text(f'''
                INSERT INTO author (name) 
                VALUES (:name)
                ON CONFLICT (name) DO NOTHING;
            ''')
    commits_stmt = text('''
                INSERT INTO repository_author (id, repository_id, pushed_at, author_id)
                VALUES (
                    :id,
                    (SELECT id FROM repository WHERE :repo_name = repo), 
                    :pushed_at, 
                    (SELECT id FROM author WHERE :author_name = name))
                ON CONFLICT (id) DO NOTHING;
    ''')
    async with engine.connect() as conn:
        await conn.execute(repo_stmt, repos)
        await conn.execute(authors_stmt, authors)
        await conn.execute(commits_stmt, commits)
        await conn.commit()


async def main():
    tasks = []
    links = parse_links()
    for link in links:
        task = parse_repo(url=link, retry=3)
        tasks.append(task)
    return await asyncio.gather(*tasks)


def handler(event, context):
    try:
        db_username = os.environ['username']
        db_password = os.environ['password']
        db_host = os.environ['host']
        db_name = os.environ['name']
        engine: Final[AsyncEngine] = create_async_engine(
            f'postgresql+asyncpg://{db_username}:{db_password}@{db_host}/{db_name}',
            poolclass=NullPool)
        repos = asyncio.run(main())
        asyncio.run(save_to_db(repos, engine))
        return {
            "statusCode": 200,
            "body": 'ok',
        }
    except Exception as ex:
        return {
            "statusCode": 500,
            "body": str(ex),
        }
