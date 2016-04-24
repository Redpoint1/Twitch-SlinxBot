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
    bot.channel_join(CHANNEL)
    bot.message('#'+CHANNEL, 'Som spat.. ahojky')
    bot.run()

sys.exit(main())
