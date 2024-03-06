from fastapi import HTTPException, status


class DataNotFound(Exception):
    pass


class RepositoryNotFoundError(HTTPException):
    def __init__(self):
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = 'repository not found'


class AuthorNotFoundError(HTTPException):
    def __init__(self):
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = 'author not found'


class BadRequestError(HTTPException):
    def __int__(self):
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = 'Invalid request'
