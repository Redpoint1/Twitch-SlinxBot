import os
import socket
import requests

from bot_irc import Message


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

    def dispatch(self, line):
        if 'PRIVMSG' in line:
            message = Message(line)
            if message.is_command:
                self.run_command(message)

    def run_command(self, command):
        command_func = getattr(self, 'command_%s' % command.command, None)
        if command_func:
            command_func(command)

    def run(self):
        readbuffer = ''
        while True:
            readbuffer = readbuffer + self.irc.recv(1024).decode()
            temp = readbuffer.split(os.linesep)
            readbuffer = temp.pop()

            for line in temp:
                line = line.rstrip()
                print(line)

                if line.startswith('PING'):
                    self.pong(line)
                else:
                    self.dispatch(line)


class Bot(BaseBot):

    def command_join(self, command):
        if command.channel != ('#'+self.nickname):
            self.message(
                command.channel,
                'This command is available only on #%s channel' % self.nickname
            )
            return

        users_channel = '#%s' % command.user
        if users_channel in self.channels:
            self.message(
                command.channel,
                'Bot is already on %s' % users_channel
            )
            return

        self.channel_join(users_channel)
        if self.is_mod(command.user):
            self.message(users_channel, 'Hi im a bot, please enjoy me. !help')
        else:
            self.message(
                users_channel,
                '@%s, probably i dont have a mod perms here!' % command.user
            )
        return
