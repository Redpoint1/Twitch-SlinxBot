import os
import re
import socket


class IRC(object):

    def __init__(self):
        self.host = None
        self.port = None
        self.username = None
        self.password = None
        self.channel = None
        self.connection = socket.socket()

    def connect(self, host, port):
        self.host = host
        self.port = port

        self.connection.connect((host, port))
        return

    def login(self, username, password):
        self.username = username
        self.password = password

        self.connection.send(('PASS %s %s' % (password, os.linesep)).encode())
        self.connection.send(('NICK %s %s' % (username, os.linesep)).encode())
        self.connection.send(('USER %s %s' % (username, os.linesep)).encode())
        return

    def allow_meta_data(self):
        self.connection.send(
            'CAP REQ :twitch.tv/membership\r\n'.encode()
        )
        self.connection.send(
            'CAP REQ :twitch.tv/tags\r\n'.encode()
        )

    def channel_join(self, channel):
        self.channel = channel

        self.connection.send(('JOIN %s %s' % (channel, os.linesep)).encode())
        return

    def channel_leave(self, channel):
        self.channel = None

        self.connection.send(('PART %s %s' % (channel, os.linesep)).encode())
        return

    def message(self, channel, text):
        self.connection.send(
            ('PRIVMSG %s :%s%s' % (channel, text, os.linesep)).encode()
        )
        return

    def pong(self, line):
        self.connection.send(
            ('PONG %s %s' % (line.split()[1], os.linesep)).encode()
        )
        return


class Message(object):
    def __init__(self, line):
        self.user, self.channel, self.message = self.parse_info(line)
        self.command, *self.args = self.parse_command(self.message)
        self.meta = self.parse_meta(line)

    def parse_info(self, line):
        # :slinxsvk!slinxsvk@slinxsvk.tmi.twitch.tv PRIVMSG #slinxsvk :test

        if 'PRIVMSG' in line:
            regex = re.search(r':([^!]+).+(#[^\s]+) :(.*)$', line, re.DOTALL)
            return regex.groups(None)
        return None, None, None

    def parse_meta(self, line):
        if 'PRIVMSG' in line:
            metas = line.split(':')[0].lstrip('@').split(';')
            meta_infos = dict()
            for meta in metas:
                key, value = meta.split('=')
                meta_infos[key.replace('-', '_')] = value.strip() or None

            return meta_infos
        return None

    def parse_command(self, message):
        if self._is_command(message):
            command = message.lstrip('!').strip()
            return command.split()
        return None, []

    @property
    def is_from_mod(self):
        return self.meta.get('mod') == '1'

    @property
    def is_command(self):
        return self._is_command(self.message)

    def _is_command(self, message):
        if isinstance(message, str) and message.startswith('!'):
            return True
        return False


class Mode(object):

    def __init__(self, line):
        self.channel, self._mode, self.user = self.parse_mode(line)

    def parse_mode(self, line):
        if 'MODE' in line:
            regex = re.search(r'(#\w+) ([+-]{1})o (\w+)', line, re.DOTALL)
            return regex.groups(None)
        return None, None, None

    @property
    def is_mod(self):
        if self._mode == '+':
            return True
        return False
