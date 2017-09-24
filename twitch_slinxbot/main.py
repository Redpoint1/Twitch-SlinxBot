import os
import sys

from .bot import MasterBot


def main():
    channel_dbs = os.path.join(os.path.curdir, 'channels')

    if not os.path.exists(channel_dbs):
        os.makedirs(channel_dbs)

    bot = MasterBot()

    host = bot.config.get('twitch', 'host')
    port = bot.config.getint('twitch', 'port')
    nick = bot.config.get('twitch', 'account')
    password = bot.config.get('twitch', 'password')
    channel = bot.config.get('twitch', 'channel')

    bot.connect(host, port)
    bot.login(nick, password)
    bot.allow_meta_data()
    bot.channel_join(channel)
    bot.message('My Lord, im available!')
    bot.run()


if __name__ == '__main__':
    sys.exit(main())
