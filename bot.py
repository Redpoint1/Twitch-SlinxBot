import re
import os
import socket
import requests


class BaseBot(object):

    def __init__(self):
        self.host = None
        self.port = None
        self.channels = []
        self.irc = None

        self.nickname = None
        self.password = None

    def connect(self, host, port):
        self.host = host
        self.port = port

        self.irc = socket.socket()
        self.irc.connect((host, port))
        return

    def login(self, nickname, password):
        self.nickname = nickname
        self.password = password

        self.irc.send(('PASS %s %s' % (password, os.linesep)).encode())
        print('PASS %s' % password)
        self.irc.send(('NICK %s %s' % (nickname, os.linesep)).encode())
        print('NICK %s' % nickname)
        self.irc.send(('USER %s %s' % (nickname, os.linesep)).encode())
        print('USER %s' % nickname)
        return

    def allow_meta_data(self):
        self.irc.send(
            'CAP REQ :twitch.tv/membership\r\n'.encode()
        )
        self.irc.send(
            'CAP REQ :twitch.tv/tags\r\n'.encode()
        )

    def channel_join(self, channel):
        self.channels.append(channel)

        self.irc.send(('JOIN %s %s' % (channel, os.linesep)).encode())
        print('JOIN %s' % channel)
        return

    def channel_leave(self, channel):
        self.channels.remove(channel)

        self.irc.send(('PART %s %s' % (channel, os.linesep)).encode())
        print('PART %s' % channel)
        return

    def message(self, channel, text):
        self.irc.send(
            ('PRIVMSG %s :%s%s' % (channel, text, os.linesep)).encode()
        )
        print('PRIVMSG %s :%s' % (channel, text))
        return

    def meta_info(self, line):
        # :slinxsvk!slinxsvk@slinxsvk.tmi.twitch.tv PRIVMSG #slinxsvk :test

        if 'PRIVMSG' in line:
            regex = re.search(r':([^!]+).+(#[^\s]+) :(.*)$', line, re.DOTALL)
            return regex.groups(None)

        return None, None, None

    def pong(self, line):
        self.irc.send(('PONG %s %s' % (line.split()[1], os.linesep)).encode())
        return

    def who_am_i(self):
        return self.nickname

    def is_mod(self, channel):
        url = 'https://tmi.twitch.tv/group/user/%s/chatters' % channel
        response = requests.get(url).json()
        moderators = response['chatters']['moderators']

        for moderator in moderators:
            if moderator == self.nickname:
                return True
        return False

    def parse_command(self, text):
        if text.startswith('!'):
            command = text.lstrip('!').strip()
            return command.split()
        return None

    def dispatch(self, line):
        user, channel, text = self.meta_info(line)
        if text:
            command_args = self.parse_command(text)
            if command_args:
                command = getattr(self, command_args[0], None)
                if command:
                    command(user, channel, text, *command_args[1:])

    def run(self):
        readbuffer = ''
        while True:
            readbuffer = readbuffer + self.irc.recv(1024).decode()
            temp = readbuffer.split(os.linesep)
            readbuffer = temp.pop()

            for line in temp:
                line = line.rstrip()
                # print(line)

                if line.startswith('PING'):
                    self.pong(line)
                else:
                    self.dispatch(line)


class Bot(BaseBot):

    def join(self, user, channel, *args):
        if channel != ('#'+self.nickname):
            self.message(
                channel,
                'This command is available only on #%s channel' % self.nickname
            )
            return

        users_channel = '#%s' % user
        if users_channel in self.channels:
            self.message(channel, 'Bot is already on %s' % users_channel)
            return

        self.channel_join(users_channel)
        if self.is_mod(user):
            self.message(users_channel, 'Hi im a bot, please enjoy me. !help')
        else:
            self.message(
                users_channel,
                '@%s, probably i dont have a mod perms here!' % user
            )
        return
