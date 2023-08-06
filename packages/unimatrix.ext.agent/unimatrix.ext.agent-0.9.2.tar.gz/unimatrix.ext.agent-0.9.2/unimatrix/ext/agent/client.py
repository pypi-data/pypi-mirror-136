"""Declares :class:`Client`."""
import abc
import contextlib
import logging

import aiohttp
from unimatrix.conf import settings
from unimatrix.ext.model import CanonicalException
from unimatrix.lib.datastructures import ImmutableDTO

from .credentials.icredentials import ICredentials


class Client(metaclass=abc.ABCMeta):
    logger: logging.Logger = logging.getLogger('uvicorn')
    audience: str = abc.abstractproperty()
    scope: set = abc.abstractproperty()

    def __init__(self, credentials: ICredentials):
        self.credentials = credentials

    async def fromjson(self, response: aiohttp.ClientResponse) -> ImmutableDTO:
        """Await the response body and deserialize it."""
        if response.status in (204, 304)\
        or (response.method == 'HEAD'):
            return None
        return ImmutableDTO.fromdict(await response.json())

    async def request(self, fn, *args, **kwargs):
        allow_failure = kwargs.pop('allow_failure', False)
        retry = kwargs.pop('retry', False)
        deserialize = kwargs.pop('deserialize', True)
        kwargs.setdefault('ssl', settings.ENABLE_SSL)
        response = await fn(*args, **kwargs)
        if 'X-Error-Code' in response.headers:
            code = response.headers['X-Error-Code']
            if retry or code != 'CREDENTIAL_EXPIRED':
                params = (await self.fromjson(response)) or {
                    'code': code
                }
                exception = CanonicalException(**params)
                exception.http_status_code = response.status
                raise exception

            # If the code is CREDENTIAL_EXPIRED or TRUST_ISSUES, then refresh
            # the access token and retry the request.
            kwargs['retry'] = True
            kwargs['deserialize'] = deserialize
            await self.refresh_credentials()
            return await self.request(fn, *args, **kwargs)
        if not allow_failure:
            response.raise_for_status()
        if deserialize:
            response = await self.fromjson(response)
        return response

    async def get(self, *args, **kwargs):
        return await self.request(self.session.get, *args, **kwargs)

    async def head(self, *args, **kwargs):
        return await self.request(self.session.head, *args, **kwargs)

    async def patch(self, *args, **kwargs):
        return await self.request(self.session.patch, *args, **kwargs)

    async def post(self, *args, **kwargs):
        return await self.request(self.session.post, *args, **kwargs)

    async def put(self, *args, **kwargs):
        return await self.request(self.session.put, *args, **kwargs)

    async def refresh_credentials(self):
        await self.credentials.apply(
            audience=self.audience,
            scope=self.scope,
            session=self.session,
            force_refresh=True
        )

    async def __aenter__(self):
        self.session = await self.credentials.apply(self.audience, self.scope)
        await self.session.__aenter__()
        return self

    async def __aexit__(self, *args, **kwargs):
        await self.session.__aexit__(*args, **kwargs)
        self.session = None
