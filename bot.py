import os
import sys
import configparser
import multiprocessing

from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database

import models as db_models

from bot_irc import Message, Mode, IRC


class Database(object):
    session = None
    engine = None
    channel = None

    def __init__(self, channel=None):
        if channel:
            self.channel = channel
            self.connect(channel)

    @classmethod
    def init_db(cls, channel=None):
        if cls.engine:
            return cls.engine

        channel = channel or cls.channel
        cls.channel = channel

        cls.engine = create_engine('sqlite:///channels/%s.sqlite' % channel)
        if not database_exists(cls.engine.url):
            create_database(cls.engine.url)
            db_models.Base.metadata.create_all(cls.engine.connect())
        return

    @classmethod
    def get_session(cls, channel=None):
        if cls.session:
            return cls.session

        channel = channel or cls.channel
        cls.channel = channel

        cls.init_db(channel)
        session_func = sessionmaker(bind=cls.engine)
        cls.session = session_func()
        return cls.session

    def connect(self, channel):
        self.get_session(channel)
        return

    def close(self):
        if self.session is not None:
            self.session.close()

    def get_or_create(self, model, **kwargs):
        instance = self.session.query(model).filter_by(**kwargs).first()
        if instance:
            return instance
        else:
            instance = model(**kwargs)
            self.session.add(instance)
            self.session.commit()
            return instance

    def command_request_by(self, username):
        user = self.get_or_create(db_models.User, username=username)
        user.last_request = datetime.utcnow()
        self.session.add(user)
        self.session.commit()

    def add_history(self, text):
        history = db_models.History(text=text)
        self.session.add(history)
        self.session.commit()


class Config(configparser.ConfigParser):

    def __init__(self):

        bot_default = {
            'host': 'irc.chat.twitch.tv',
            'port': '6667',
            'limit_as_user': '20',
            'limit_as_mod': '100',
            'timeout_per_user': '30'
        }

        super(Config, self).__init__(bot_default)


class BaseBot(object):

    def __init__(self):
        self.irc = IRC()
        self.is_mod = False
        self.config = Config()
        self.db = Database()
        config_path = os.path.join(os.curdir, 'twitch.cfg')
        if os.path.exists(config_path):
            self.config.read(config_path)
        else:
            raise configparser.ParsingError('Unable to find config file')

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
        self.db.connect(channel)
        return

    def channel_leave(self):
        self.irc.channel_leave()
        return

    def message(self, text):
        self.irc.message(text)
        if self.irc.channel is not None:
            self.db.add_history(text)
        return

    def pong(self, line):
        self.irc.pong(line)
        return

    def dispatch(self, line):
        if 'PRIVMSG' in line:
            message = Message(line)
            if message.is_command:
                self.db.command_request_by(message.user)
                self.run_command(message)
        if 'MODE' in line:
            operator = Mode(line)
            if operator.channel == self.channel:
                if operator.user == self.username:
                    self.is_mod = operator.is_mod
                return
            print('Unexpected channel')

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
        print("%s: I was enslaved." % multiprocessing.current_process().name)
        super(SlaveBot, self).__init__()

    def command_leave(self, command):
        if command.channel == ('#' + self.username):
            return

        if command.is_from_mod:
            sys.exit(-1)


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
        users_channel = command.user

        if users_channel == self.channel:
            self.message('Im already on this channel!')
            return

        # if users_channel != self.channel:
        #     # TODO process list name aka channel name check
        #     self.message(
        #         'Bot is already on %s' % users_channel
        #     )
        #     return

        slave = multiprocessing.Process(
            target=self.enslave,
            args=(self.host, self.port, self.username, self.password,
                  users_channel))
        self.slaves.append(slave)
        slave.start()
        return
