import sys

from bot import Bot

NICK = 'XX'
CHANNEL = 'XX'
PASS = 'XX'
HOST = 'irc.chat.twitch.tv'
PORT = 6667


def main():
    bot = Bot()
    bot.connect(HOST, PORT)
    bot.login(NICK, PASS)
    bot.allow_meta_data()
    bot.channel_join(CHANNEL)
    bot.message(CHANNEL, 'Im again available. Use me!')
    bot.run()

sys.exit(main())
