import asyncio
import base64

import aiohttp

from .base import WebRequest
from .message import *


class Contact(WebRequest):

    def __init__(self, client_data, pk, authorizationStatus, avatarMd5, group, hashedPk, isFriend, nick, status):
        self._pk = pk
        self._client_data = client_data
        self._authorization_status = authorizationStatus
        self._avatar_md5 = avatarMd5
        self._group = group
        self._hashed_pk = hashedPk
        self._is_friend = isFriend
        self._nick = nick
        self._status = status

    def __str__(self):
        return self._nick

    @property
    def pk(self):
        return self._pk

    async def send(self, message=None):
        data = {
                "method": "sendInstantMessage",
                "to": self._pk,
                "text": message
                }
        await self._get(self._client_data, **data)

    @property
    def authorization_status(self):
        return self._authorization_status

    @property
    def avatar_md5(self):
        return self._avatar_md5

    @property
    def hashed_pk(self):
        return self._hashed_pk

    @property
    def is_friend(self):
        return self.is_friend

    @property
    def name(self):
        return self._nick

    async def avatar(self):
        base64_avatar = await self._get(self._client_data, pk=self._pk, coder='BASE64', format='JPG')
        bytes_avatar = base64.b64decode(base64_avatar)
        return bytes_avatar

    async def fetch_messages(self, old_first=True):
        i = -1 if old_first else 1
        messages = await self._get(self._client_data, method='getContactMessages', pk=self._pk)
        for message_data in messages[::i]:
            message = Message(client_data=self._client_data, **message_data)
            yield message
