import asyncio
from collections import namedtuple

import aiohttp

from .message import Message
from .contact import Contact
from .channel import Channel
from .base import *


class Client(WebRequest):
    def __init__(self):
        self._messages_types = {'newOutgoingChannelMessage', 'newChannelMessage',
                                'newInstantMessage', 'newOutgoingInstantMessage'}
        self.token = None
        self.url = None
        self.api_port = None
        self.websocket_port = None
        self.loop = None
        self._session = None
        self._contacts = {}
        self._channels = {}
        self._full_api_url = None
        self._own_contact = None
        self._Event = namedtuple('Event', ['type', 'data'])

    async def _get_own_contact(self):
        resp = await self._get(self._client_data, method='getOwnContact')
        self._own_contact = Contact(self._client_data, **resp)

    async def register_contact(self, pk):
        raw_resp = await self._get(self._client_data, method='getContacts', filter=pk)
        contact_info = raw_resp[0]
        contact = Contact(self._client_data, **contact_info)
        self.contacts[pk] = contact
        self._client_data.contacts[pk] = contact
        return contact

    async def _get_contacts(self):
        raw_resp = await self._get(self._client_data, method='getContacts', filter='')
        for contact_info in raw_resp:
            contact = Contact(self._client_data, **contact_info)
            self.contacts[contact.pk] = contact
            self._client_data.contacts[contact.pk] = contact

    async def register_channel(self, channel_id):
        channel_info = await self._get(self._client_data, method='getChannelInfo', channelid=channel_id)
        # print(raw_resp)
        channel_info.update({'channelid': channel_id})
        channel = Channel(self._client_data, **channel_info)
        self._channels[channel_id] = channel
        self._client_data.channels[channel_id] = channel
        return channel

    async def _get_channels(self):
        raw_resp = await self._get(self._client_data, method='getChannels', filter='', channel_type=0)
        for channel in raw_resp:
            await self.register_channel(channel['channelid'])

    def event(self, coro):
        if not asyncio.iscoroutinefunction(coro):
            raise TypeError('event registered must be a coroutine function')
        self.__setattr__(coro.__name__, coro)
        return coro

    async def _get_websocket_state(self, session):
        params = {
            "method": "getWebSocketState",
            "token": self.token
        }
        async with session.get(self._full_api_url, json=params) as raw_resp:
            assert raw_resp.status == 200
            resp = await raw_resp.json()
            return resp['result']

    async def _set_websocket_state(self, session, enabled, port):
        params = {
            "method": "setWebSocketState",
            "params": {
                "enabled": enabled,
                "port": port
            },
            "token": self.token
        }
        async with session.get(self._full_api_url, json=params) as raw_resp:
            assert raw_resp.status == 200
            resp = await raw_resp.json()
            return resp['result']

    async def _activate_websocket(self, session):
        websocket_state = await self._get_websocket_state(session)
        if not websocket_state:
            print(f'Start websocket on {self.websocket_port} port!')
            await self._set_websocket_state(session, True, self.websocket_port)
            print('Websocket started!')
        else:
            print(f'Websocket already started on port {self.websocket_port}')

    async def _websocket_connect(self, session):
        async with session.ws_connect(f'ws://{self.url}:{self.websocket_port}/UtopiaWSS?token={self.token}', autoclose=False) as ws:
            if self.__getattribute__('on_ready'):
                coro = self.__getattribute__('on_ready')
                self.loop.create_task(coro())

            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    message = msg.json()
                    print(message)
                    yield message
                if msg.type == aiohttp.WSMsgType.ERROR:
                    break

    async def _handle_ws_message(self):
        async for message in self._websocket_connect(self._ws_session):
            message_type = None
            if message['type'] in self._messages_types:
                message_type = 'on_message'

            elif message['type'] == 'channelJoinChanged':
                if message['data']['is_joined']:
                    message_type = 'on_channel_join'

                if not message['data']['is_joined']:
                    message_type = 'on_channel_leave'

            elif message['type'] == 'newAuthorization':
                message_type = 'on_auth_request'

            if message_type:
                message['data'].update({'type': message['type']})
                event = self._Event(message_type, message['data'])
                yield event

    async def _listen(self):
        async for event in self._handle_ws_message():
            if event.data['type'] in self._messages_types:
                if self.__getattribute__(event.type):
                    coro = self.__getattribute__(event.type)
                    message = Message(self._client_data, **event.data)
                    self.loop.create_task(coro(message))

            elif event.type == 'on_channel_join':
                if self.__getattribute__(event.type):
                    coro = self.__getattribute__(event.type)
                    # channel = await self.register_channel(channel_id)
                    self.loop.create_task(coro())

            elif event.type == 'on_channel_leave':
                if self.__getattribute__(event.type):
                    coro = self.__getattribute__(event.type)
                    # channel = await self.register_channel(channel_id)
                    self.loop.create_task(coro())

            elif event.type == 'on_auth_request':
                if self.__getattribute__(event.type):
                    coro = self.__getattribute__(event.type)
                    contact = await self.register_contact(event.data)
                    self.loop.create_task(coro(contact))

    def _create_data_class(self):
        data = {
            'token': self.token,
            'url': self.url,
            'api_port': self.api_port,
            'websocket_port': self.websocket_port,
            'session': self._session,
            'loop': self.loop
        }
        self._client_data = ClientData(**data)

    async def _get_media(self):
        self._create_data_class()
        await self._get_contacts()
        await self._get_channels()
        await self._get_own_contact()

    async def connect(self, loop=None):
        async with aiohttp.ClientSession(loop=loop) as session, aiohttp.ClientSession(loop=loop) as ws_session:
            await self._activate_websocket(session)
            self._session = session
            self._ws_session = ws_session
            await self._get_media()
            await self._listen()

    def run(self, token, url='127.0.0.1', api_port=20000, websocket_port=30000):
        self.token = token
        self.url = url
        self.api_port = api_port
        self.websocket_port = websocket_port
        self._full_api_url = f'http://{self.url}:{self.api_port}/api/1.0'

        loop = asyncio.get_event_loop()
        self.loop = loop
        loop.create_task(self.connect(loop))
        loop.run_forever()

    @property
    def contacts(self):
        return self._contacts

    @property
    def contact(self):
        return self._own_contact

    @property
    def channels(self):
        return self._channels

    async def status(self):
        pass

    def get_contact(self, pk):
        return self._contacts.get(pk)

    async def get_channel(self, channel_id):
        if channel_id in self._channels:
            return self._channels.get(channel_id)
        else:
            try:
                return await self.register_channel(channel_id)
            except KeyError:
                raise KeyError('Wrong channel_id!')
