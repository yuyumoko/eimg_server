import asyncio
import functools
from enum import Enum
from types import TracebackType
from typing import Any, Optional, Type, TypeVar

import aiohttp
import ujson

T = TypeVar("T")


class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"


class HTTPSession:
    def __init__(self, headers=None):
        self.headers = headers

    async def _create(self) -> aiohttp.ClientSession:
        return aiohttp.ClientSession(
            headers=self.headers,
            connector=aiohttp.TCPConnector(ssl=False),
            timeout=aiohttp.ClientTimeout(total=3),
            json_serialize=ujson.dumps,
        )

    async def __aenter__(self) -> aiohttp.ClientSession:
        session_object = await self._create()
        self.session = await session_object.__aenter__()
        return self.session

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        await self.session.close()

    def Session(f):
        @functools.wraps(f)
        async def wrapper(
            self,
            *args: Any,
            session: Optional[aiohttp.ClientSession] = None,
            **kwargs: Any
        ) -> T:
            if session is None:
                async with self._session as session:
                    return await f(self, *args, session=session, **kwargs)
            return await f(self, *args, session=session, **kwargs)

        return wrapper
