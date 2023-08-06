import requests
import time
import asyncio

from ..exceptions import ScopeException
from ..constants import base_url


class AsynchronousHTTPHandler:
    def __init__(self, auth, client, limit_per_second=1):
        self.auth = auth
        self.client = client
        self.rate_limit = RateLimiter(limit_per_second)

    def get_headers(self, **kwargs):
        headers = {
            'Authorization': f'Bearer {self.auth.token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            **{str(key): str(value) for key, value in kwargs.items() if value is not None}
        }
        return headers

    async def _make_request(self, method, path, data=None, headers=None, stream=False, **kwargs):
        if headers is None:
            headers = {}
        if data is None:
            data = {}

        if not self.rate_limit.can_request:
            await self.rate_limit.wait()

        scope_required = path.scope
        if scope_required.scopes not in self.client.auth.scope:
            raise ScopeException(f"You don't have the {scope_required} scope, which is required to do this action.")

        headers = self.get_headers(**headers)
        response = getattr(requests, method)(base_url + path.path, headers=headers, data=data, stream=stream, params=kwargs)
        self.rate_limit.request_used()
        response.raise_for_status()
        return response.json()

    async def get(self, path, data=None, headers=None, stream=False, **kwargs):
        return await self._make_request('get', path, data=data, headers=headers, stream=stream, **kwargs)

    async def post(self, path, data=None, headers=None, stream=False, **kwargs):
        return await self._make_request('post', path, data=data, headers=headers, stream=stream, **kwargs)

    async def delete(self, path, data=None, headers=None, stream=False, **kwargs):
        return await self._make_request('delete', path, data=data, headers=headers, stream=stream, **kwargs)

    async def patch(self, path, data=None, headers=None, stream=False, **kwargs):
        return await self._make_request('patch', path, data=data, headers=headers, stream=stream, **kwargs)

    async def put(self, path, data=None, headers=None, stream=False, **kwargs):
        return await self._make_request('put', path, data=data, headers=headers, stream=stream, **kwargs)


class RateLimiter:
    def __init__(self, limit_per_second=1):
        self.limit = limit_per_second
        self.last_request = time.perf_counter() - self.limit

    def request_used(self):
        self.last_request = time.perf_counter()

    async def wait(self):
        await asyncio.sleep(self.limit-(time.perf_counter()-self.last_request))

    @property
    def can_request(self):
        return time.perf_counter()-self.last_request >= self.limit
