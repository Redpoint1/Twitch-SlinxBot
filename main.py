import os
import sys
import subprocess

from bot import Bot

NICK = 'XX'
CHANNEL = 'XX'
PASS = 'XX'
HOST = 'irc.chat.twitch.tv'
PORT = 6667


def main():
    subprocess.Popen(['celery', '-A', 'twitch', 'worker'],
                     stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL,
                     shell=True)

    pid_file = os.path.join(os.path.curdir, 'celerybeat.pid')
    if os.path.exists(pid_file):
        os.remove(pid_file)
    subprocess.Popen(['celery', '-A', 'twitch', 'beat', '-l', 'info'],
                     stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL,
                     shell=True)

    bot = Bot()
    bot.connect(HOST, PORT)
    bot.login(NICK, PASS)
    bot.allow_meta_data()
    bot.channel_join(CHANNEL)
    bot.message(CHANNEL, 'Im again available. Use me!')
    bot.run()

if __name__ == '__main__':
    sys.exit(main())
