from datetime import datetime

from .base import WebRequest
from .message import *


class Channel(WebRequest):
    def __init__(self, client_data, **kwargs):
        self._client_data = client_data

        self._hide_in_common_list = kwargs['HideInCommonList']
        self._created = kwargs['created']
        self._geotag = kwargs['geotag']
        self._hashtags = kwargs['hashtags']
        self._languages = kwargs['languages']
        self._modified = kwargs['modified']
        self._owner_pk = kwargs['owner']
        self._is_readonly = kwargs['readonly']
        self._is_readonly_privacy = kwargs['readonly_privacy']
        self._title = kwargs['title']
        self._description = kwargs['description']
        self._type = kwargs['type']
        self._id = kwargs['channelid']

    def __str__(self):
        return self._title

    @property
    def id(self):
        return self._id

    @property
    def is_hidden(self):
        return self._hide_in_common_list

    @property
    def create_time(self):
        return datetime.fromisoformat(self._created).timestamp()

    @property
    def hashtags(self):
        return self._hashtags.split(',')

    @property
    def languages(self):
        return self._languages.split(',')

    @property
    def modified_time(self):
        return datetime.fromisoformat(self._modified).timestamp()

    @property
    def owner_pk(self):
        return self.owner_pk

    @property
    def is_readonly(self):
        return self._is_readonly

    @property
    def name(self):
        return self._title

    @property
    def description(self):
        return self._description

    @property
    def type(self):
        return self._type

    async def send(self, message=None, attachment=None):
        data = {
            'method': 'sendChannelMessage',
            'channelid': self._id,
            'message': message
        }
        await self._get(self._client_data, **data)

    async def join(self, password=None):
        await self._get(self._client_data, method='joinChannel', ident=self._id, password=password)

    async def leave(self):
        await self._get(self._client_data, method="leaveChannel", channelid=self._id)

    async def fetch_messages(self, old_first=True):
        i = -1 if old_first else 1
        messages = await self._get(self._client_data, method='getChannelMessages', channelid=self._id)
        for message_data in messages[::i]:
            message = Message(client_data=self._client_data, **message_data)
            yield message
