import os
import sys
import subprocess

from bot import MasterBot


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
    bot.message(channel, 'My Lord, im available!')
    bot.run()

if __name__ == '__main__':
    sys.exit(main())
