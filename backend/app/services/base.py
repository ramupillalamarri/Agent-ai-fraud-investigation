from typing import Generic, TypeVar
from app.repositories.base import BaseRepository

RepositoryType = TypeVar("RepositoryType", bound=BaseRepository)


class BaseService(Generic[RepositoryType]):
    """Base application service implementing business orchestration.

    Acts as the entrypoint for executing business rules and transactions.
    """

    def __init__(self, repository: RepositoryType):
        self.repository = repository
