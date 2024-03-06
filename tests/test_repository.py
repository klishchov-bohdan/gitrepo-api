import datetime

from fastapi import FastAPI
from httpx import AsyncClient

from app.exceptions import DataNotFound
from app.utils.uow import UnitOfWork


class TestRepository:
    async def test_get_all_repositories(self, ac: AsyncClient, api: FastAPI, uow: UnitOfWork):
        async with uow:
            await uow.repository_repo.add_one({
                    'repo': 'repo_name',
                    'owner': 'owner_name',
                    'stars': 28723,
                    'watchers': 7283,
                    'forks': 724,
                    'open_issues': 437,
                    'language': 'Python',
                })
            await uow.commit()
        req_url = api.url_path_for('get_repositories')
        response = await ac.get(req_url, follow_redirects=True)
        assert response.status_code == 200, 'Can`t get all repositories'
        assert response.text[0] == '[' and response.text[-1] == ']', 'Response json is not a list'
        async with uow:
            result = await uow.repository_repo.find_all()
        repos = [repo for repo in result]
        for idx, repo in enumerate(repos):
            assert repo['repo'] == response.json()[idx]['repo'], 'Repo name is not equal'
            assert repo['owner'] == response.json()[idx]['owner'], 'Repo owner is not equal'
            assert repo['stars'] == response.json()[idx]['stars'], 'Repo stars is not equal'

    async def test_get_top100_repositories(self, ac: AsyncClient, api: FastAPI, uow: UnitOfWork):
        async with uow:
            await uow.repository_repo.add_one({
                    'repo': 'repo_name10',
                    'owner': 'owner_name10',
                    'stars': 287,
                    'watchers': 7283,
                    'forks': 724,
                    'open_issues': 437,
                    'language': 'Python',
                })
            await uow.commit()
        req_url = api.url_path_for('get_top100_repositories')
        response = await ac.get(req_url+'?sort_by=stars&sort_strategy=DESC', follow_redirects=True)
        assert response.status_code == 200, 'Can`t get top 100 repositories'
        assert response.text[0] == '[' and response.text[-1] == ']', 'Response json is not a list'
        assert response.json()[0]['stars'] > response.json()[-1]['stars'], 'Sorting error'

    async def test_create_repository(self, ac: AsyncClient, api: FastAPI, uow: UnitOfWork):
        req_url = api.url_path_for('create_repository')
        repo = {
            'repo': 'repo_name2',
            'owner': 'owner_name2',
            'stars': 28723,
            'watchers': 7283,
            'forks': 724,
            'open_issues': 437,
            'language': 'Python',
        }
        response = await ac.post(req_url, follow_redirects=True,
                                 json=repo)
        assert response.status_code == 201, 'Can`t create repo'
        assert response.json()['repository_id'], 'Response haven`t a field repo'
        async with uow:
            created_repo = await uow.repository_repo.find_one(response.json()['repository_id'])
        assert created_repo['repo'] == repo['repo'], 'Repo name is not equal'
        assert created_repo['owner'] == repo['owner'], 'Repo owner is not equal'
        assert created_repo['stars'] == repo['stars'], 'Repo stars is not equal'

    async def test_get_repository(self, ac: AsyncClient, api: FastAPI, uow: UnitOfWork):
        repo = {
            'repo': 'repo_name5',
            'owner': 'owner_name5',
            'stars': 28723,
            'watchers': 7283,
            'forks': 724,
            'open_issues': 437,
            'language': 'Python',
        }
        async with uow:
            repo_id = await uow.repository_repo.add_one(repo)
            await uow.commit()
        req_url = api.url_path_for('get_repository', repository_id=repo_id)
        response = await ac.get(req_url, follow_redirects=True)
        assert response.status_code == 200, 'Can`t get repo by id'
        assert response.json()['repo'], 'Response haven`t a field repo'
        assert repo['repo'] == response.json()['repo'], 'Repo name is not equal'

    async def test_get_repository_activity(self, ac: AsyncClient, api: FastAPI, uow: UnitOfWork):
        repo = {
            'repo': 'repo_name34',
            'owner': 'owner_name34',
            'stars': 28723,
            'watchers': 7283,
            'forks': 724,
            'open_issues': 437,
            'language': 'Python',
        }
        author = {
            'name': 'John'
        }
        date = datetime.datetime(2024, 1, 1)
        async with uow:
            repo_id = await uow.repository_repo.add_one(repo)
            author_id = await uow.author_repo.add_one(author)
            await uow.repository_author_repo.add_one({
                'id': 'some_awesome_id',
                'repository_id': repo_id,
                'author_id': author_id,
                'pushed_at': date
            })
            await uow.commit()
        req_url = api.url_path_for('get_repository_activity', owner=repo['owner'], repo=repo['repo'])
        response = await ac.get(req_url+'?since=2020-01-01&until=2024-02-02', follow_redirects=True)
        assert response.status_code == 200, 'Can`t get repo activity by id'
        assert response.json()[0]['date'], 'Response date not exists'

    async def test_update_repository(self, ac: AsyncClient, api: FastAPI, uow: UnitOfWork):
        repo = {
            'repo': 'repo_name3',
            'owner': 'owner_name3',
            'stars': 223,
            'watchers': 7283,
            'forks': 724,
            'open_issues': 437,
            'language': 'Python',
        }
        req_url = api.url_path_for('update_repository', repository_id=1)
        response = await ac.patch(req_url, follow_redirects=True, json=repo)
        assert response.status_code == 200, 'Can`t update repository'
        assert response.json()['repository_id'], 'Response haven`t a field id'
        async with uow:
            updated_repo = await uow.repository_repo.find_one(response.json()['repository_id'])
        assert updated_repo['repo'] == repo['repo'], 'Repo name is not equal'
        assert updated_repo['owner'] == repo['owner'], 'Repo owner is not equal'
        assert updated_repo['stars'] == repo['stars'], 'Repo stars is not equal'

    async def test_delete_repository(self, ac: AsyncClient, api: FastAPI, uow: UnitOfWork):
        repo = {
            'repo': 'repo_name4',
            'owner': 'owner_name4',
            'stars': 22332,
            'watchers': 72383,
            'forks': 7244,
            'open_issues': 2437,
            'language': 'Python',
        }
        async with uow:
            repo_id = await uow.repository_repo.add_one(repo)
            await uow.commit()
        req_url = api.url_path_for('delete_repository', repository_id=repo_id)
        response = await ac.delete(req_url, follow_redirects=True)
        assert response.status_code == 200, 'Can`t delete repo by id'
        async with uow:
            try:
                deleted_repo = await uow.repository_repo.find_one(response.json()['repository_id'])
                assert deleted_repo is None, 'Can`t delete repo'
            except DataNotFound:
                pass
