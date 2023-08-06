from __future__ import (
    annotations,
)

from abc import (
    ABC,
    abstractmethod,
)
from contextvars import (
    ContextVar,
)
from typing import (
    Any,
    Final,
    Optional,
)
from uuid import (
    UUID,
)

from ..exceptions import (
    MinosException,
    NotHasContentException,
    NotHasParamsException,
)

REQUEST_USER_CONTEXT_VAR: Final[ContextVar[Optional[UUID]]] = ContextVar("user", default=None)


class Request(ABC):
    """Request interface."""

    @property
    @abstractmethod
    def user(self) -> Optional[UUID]:
        """
        Returns the UUID of the user making the Request.
        """
        raise NotImplementedError

    async def content(self, **kwargs) -> Any:
        """Get the request content.

        :param kwargs: Additional named arguments.
        :return: The request content.
        """
        if not self.has_content:
            raise NotHasContentException(f"{self!r} has not content.")
        return await self._content(**kwargs)

    @property
    @abstractmethod
    def has_content(self) -> bool:
        """Check if the request has content.

        :return: ``True`` if it has content or ``False`` otherwise.
        """
        raise NotImplementedError

    async def _content(self, **kwargs) -> Any:
        raise RuntimeError(
            f"{type(self).__name__}._content must be implemented if {type(self).__name__}.has_content returns {True!r}."
        )

    async def params(self, **kwargs) -> dict[str, Any]:
        """Get the request params.

        :param kwargs: Additional named arguments.
        :return: The request params.
        """
        if not self.has_params:
            raise NotHasParamsException(f"{self!r} has not params.")
        return await self._params(**kwargs)

    @property
    @abstractmethod
    def has_params(self) -> bool:
        """Check if the request has params.

        :return: ``True`` if it has params or ``False`` otherwise.
        """
        raise NotImplementedError

    async def _params(self, **kwargs) -> dict[str, Any]:
        raise RuntimeError(
            f"{type(self).__name__}._params must be implemented if '{type(self).__name__}.has_params returns {True!r}."
        )

    @abstractmethod
    def __eq__(self, other: Request) -> bool:
        raise NotImplementedError

    @abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError


sentinel = object()


class Response:
    """Response definition."""

    __slots__ = "_data"

    def __init__(self, data: Any = sentinel):
        self._data = data

    # noinspection PyUnusedLocal
    async def content(self, **kwargs) -> Any:
        """Response content.

        :param kwargs: Additional named arguments.
        :return: A list of items.
        """
        return self._data

    @property
    def has_content(self) -> bool:
        """Check if the request has content.

        :return: ``True`` if it has content or ``False`` otherwise.
        """
        return self._data is not sentinel

    def __eq__(self, other: Response) -> bool:
        return type(self) == type(other) and self._data == other._data

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._data!r})"

    def __hash__(self):
        return hash(self._data)


class ResponseException(MinosException):
    """Response Exception class."""
