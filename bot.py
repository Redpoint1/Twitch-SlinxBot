import re
import os
import socket
import requests


class Bot(object):

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

    def channel_join(self, channel):
        self.channels.append(channel)

        self.irc.send(('JOIN #%s %s' % (channel, os.linesep)).encode())
        print('JOIN #%s' % channel)
        return

    def channel_leave(self, channel):
        self.channels.remove(channel)

        self.irc.send(('PART #%s %s' % (channel, os.linesep)).encode())
        print('PART #%s' % channel)
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
            regex = re.search(r'^:([^!]+).+(#[^\s]+) :(.*)$', line, re.DOTALL)
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
                    user, channel, text = self.meta_info(line)
                    if user:
                        print('%s: %s -> %s' % (channel, user, text))
