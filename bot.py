import os
import requests
import multiprocessing

from bot_irc import Message, IRC


class BaseBot(object):

    def __init__(self):
        self.irc = IRC()

    @property
    def host(self):
        return self.irc.host

    @property
    def port(self):
        return self.irc.port

    @property
    def username(self):
        return self.irc.username

    @property
    def password(self):
        return self.irc.password

    @property
    def channel(self):
        return self.irc.channel

    def connect(self, host, port):
        self.irc.connect(host, port)
        return

    def login(self, username, password):
        self.irc.login(username, password)
        return

    def allow_meta_data(self):
        self.irc.allow_meta_data()
        return

    def channel_join(self, channel):
        self.irc.channel_join(channel)
        return

    def channel_leave(self, channel):
        self.irc.channel_leave(channel)
        return

    def message(self, channel, text):
        self.irc.message(channel, text)
        return

    def pong(self, line):
        self.irc.pong(line)
        return

    def is_mod(self, channel):
        url = 'https://tmi.twitch.tv/group/user/%s/chatters' % channel
        response = requests.get(url).json()
        moderators = response['chatters']['moderators']

        for moderator in moderators:
            if moderator == self.username:
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
            readbuffer = readbuffer + self.irc.connection.recv(1024).decode()
            temp = readbuffer.split(os.linesep)
            readbuffer = temp.pop()

            for line in temp:
                line = line.rstrip()
                print(line)

                if line.startswith('PING'):
                    self.pong(line)
                else:
                    self.dispatch(line)


class SlaveBot(BaseBot):

    def __init__(self):
        print("I was enslaved. %s" % multiprocessing.current_process().name)
        super(SlaveBot, self).__init__()

    def command_leave(self):
        pass


class MasterBot(SlaveBot):

    def __init__(self):
        self.slaves = []
        super(SlaveBot, self).__init__()

    def enslave(self, host, port, nick, password, channel):
        bot = SlaveBot()
        bot.connect(host, port)
        bot.login(nick, password)
        bot.allow_meta_data()
        bot.channel_join(channel)
        bot.run()

    def command_join(self, command):
        if command.channel != ('#'+self.username):
            return

        users_channel = '#%s' % command.user
        if users_channel in self.channel:
            # process list name aka channel name check
            self.message(
                command.channel,
                'Bot is already on %s' % users_channel
            )
            return

        slave = multiprocessing.Process(
            target=self.enslave,
            args=(self.host, self.port, self.username, self.password,
                  users_channel))
        self.slaves.append(slave)
        slave.start()
        return
