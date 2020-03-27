import asyncio

import aiohttp


class ClientData:
    def __init__(self, token, url, api_port, websocket_port, session, loop):
        self.token = token
        self.url = url
        self.api_port = api_port
        self.websocket_port = websocket_port
        self.session = session
        self.loop = loop
        self.contacts = {}
        self.channels = {}


class WebRequest:

    @staticmethod
    async def _get(client_data, **kwargs):
        send_url = f'http://{client_data.url}:{client_data.api_port}/api/1.0'
        data = {
            'method': kwargs['method'],
            'params': {key: value for key, value in kwargs.items() if key != 'method'},
            'token': client_data.token
        }
        async with client_data.session.get(send_url, json=data) as resp:
            response = await resp.json()
            if 'extended' in kwargs:
                return response
            else:
                return response['result']


class Status(WebRequest):
    def __init__(self, status, mood, client_data=None):
        if status in {'Available', 'Away', 'DoNotDisturb', 'Invisible', 'Offline'}:
            self.status = status
        else:
            raise TypeError('Status must be one of "Available", "Away", "DoNotDisturb", "Invisible", "Offline"')
        self.mood = mood
        self._client_data = client_data

    async def get(self):
        self.status, self.mood = await self._get(self._client_data, method='getProfileStatus')
        return self

    async def set(self, status):
        self.status, self.mood = status.status, status.mood
        await self._get(self._client_data, method='setProfileStatus', status=status.status, mood=status.mood)
        return self
