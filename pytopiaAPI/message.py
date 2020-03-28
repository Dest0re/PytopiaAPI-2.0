import asyncio
from datetime import datetime

import aiohttp

from .base import WebRequest


class Message(WebRequest):
    def __init__(self, client_data, dateTime, isIncoming, messageType, metaData, nick, text, pk,
                 type=None, hashedPk=None, topicId=None, channel=None, channelid=None, id=None, readDateTime=None,
                 receivedDateTime=None):
        self._date_time = dateTime
        self._hashed_pk = hashedPk
        self._is_incoming = isIncoming
        self._message_type = messageType
        self._metadata = metaData
        self._nick = nick
        self._text = text
        self._topic_id = topicId
        self._type = type
        self._channel_name = channel
        self._channel_id = channelid
        self._pk = pk
        self._id = id
        self._read_date_time = readDateTime
        self._received_date_time = receivedDateTime
        self._client_data = client_data
        self._quote = None
        if self._metadata:
            if 'type' in self._metadata:
                if self._metadata['type'] == 'quote':
                    self._quote = {}
                    self._text = self._metadata['data']['text']
                    self._quote['date_time'] = datetime.fromisoformat(self._metadata['data']['dateTime']).timestamp()
                    self._quote['is_channel'] = self._metadata['data']['isChannel']
                    if self._quote['is_channel']:
                        self._quote['hashed_pk'] = self._metadata['data']['hexPublicKey']
                        self._quote['pk'] = None
                    else:
                        self._quote['pk'] = self._metadata['data']['hexPublicKey']
                        self._quote['hashed_pk'] = None
                    self._quote['author'] = self._metadata['data']['nick']
                    self._quote['text'] = self._metadata['data']['quote']

    def __str__(self):
        return self.text

    @property
    def text(self):
        if self._message_type != 6:
            if self._text:
                return self._text
        else:
            return ''

    @property
    def date_time(self):
        return datetime.fromisoformat(self._date_time).timestamp()

    @property
    def is_incoming(self):
        return self._is_incoming

    @property
    def message_type(self):
        return self._message_type

    @property
    def metadata(self):
        return self._metadata

    @property
    def author(self):
        return self._nick

    @property
    def type(self):
        return self._type

    @property
    def channel(self):
        if self.type.endswith('InstantMessage'):
            return self._client_data.contacts.get(self._pk)
        elif self.type.endswith('ChannelMessage'):
            if self._channel_id in self._client_data.channels:
                return self._client_data.channels.get(self._channel_id)
            else:
                raise TypeError('The channel is not registered.')
