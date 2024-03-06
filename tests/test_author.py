from fastapi import FastAPI
from httpx import AsyncClient

from app.exceptions import DataNotFound
from app.utils.uow import UnitOfWork


class TestAuthor:
    async def test_get_all_authors(self, ac: AsyncClient, api: FastAPI, uow: UnitOfWork):
        async with uow:
            await uow.author_repo.add_one({
                'name': 'author_name',
            })
            await uow.commit()
        req_url = api.url_path_for('get_authors')
        response = await ac.get(req_url, follow_redirects=True)
        assert response.status_code == 200, 'Can`t get all authors'
        assert response.text[0] == '[' and response.text[-1] == ']', 'Response json is not a list'
        async with uow:
            result = await uow.author_repo.find_all()
        authors = [author for author in result]
        for idx, author in enumerate(authors):
            assert author['name'] == response.json()[idx]['name'], 'Author name is not equal'

    async def test_create_author(self, ac: AsyncClient, api: FastAPI, uow: UnitOfWork):
        req_url = api.url_path_for('create_author')
        author = {
            'name': 'author_name2',
        }
        response = await ac.post(req_url, follow_redirects=True, json=author)
        assert response.status_code == 201, 'Can`t create author'
        assert response.json()['author_id'], 'Response haven`t a field author_id'
        async with uow:
            created_author = await uow.author_repo.find_one(response.json()['author_id'])
        assert created_author['name'] == author['name'], 'Author name is not equal'

    async def test_get_author(self, ac: AsyncClient, api: FastAPI, uow: UnitOfWork):
        author = {
            'name': 'author_name3',
        }
        async with uow:
            author_id = await uow.author_repo.add_one(author)
            await uow.commit()
        req_url = api.url_path_for('get_author', author_id=author_id)
        response = await ac.get(req_url, follow_redirects=True)
        assert response.status_code == 200, 'Can`t get author by id'
        assert response.json()['name'], 'Response haven`t a field name'
        assert author['name'] == response.json()['name'], 'Author name is not equal'

    async def test_update_author(self, ac: AsyncClient, api: FastAPI, uow: UnitOfWork):
        author = {
            'name': 'author_name4',
        }
        req_url = api.url_path_for('update_author', author_id=1)
        response = await ac.patch(req_url, follow_redirects=True, json=author)
        assert response.status_code == 200, 'Can`t update author'
        assert response.json()['author_id'], 'Response haven`t a field id'
        async with uow:
            updated_author = await uow.author_repo.find_one(response.json()['author_id'])
        assert updated_author['name'] == author['name'], 'Author name is not equal'

    async def test_delete_author(self, ac: AsyncClient, api: FastAPI, uow: UnitOfWork):
        author = {
            'name': 'author_name5',
        }
        async with uow:
            author_id = await uow.author_repo.add_one(author)
            await uow.commit()
        req_url = api.url_path_for('delete_author', author_id=author_id)
        response = await ac.delete(req_url, follow_redirects=True)
        assert response.status_code == 200, 'Can`t delete author by id'
        async with uow:
            try:
                deleted_author = await uow.author_repo.find_one(response.json()['author_id'])
                assert deleted_author is None, 'Can`t delete author'
            except DataNotFound:
                pass
