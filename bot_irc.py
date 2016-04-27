import re


class Message(object):
    def __init__(self, line):
        self.user, self.channel, self.message = self.parse_info(line)
        self.command, *self.args = self.parse_command(self.message)
        self.meta = self.parse_meta(line)

    def parse_info(self, line):
        # :slinxsvk!slinxsvk@slinxsvk.tmi.twitch.tv PRIVMSG #slinxsvk :test

        if 'PRIVMSG' in line:
            regex = re.search(r':([^!]+).+(#[^\s]+) :(.*)$', line, re.DOTALL)
            return regex.groups(None)
        return None, None, None

    def parse_meta(self, line):
        if 'PRIVMSG' in line:
            metas = line.split(':')[0].lstrip('@').split(';')
            meta_infos = dict()
            for meta in metas:
                key, value = meta.split('=')
                meta_infos[key.replace('-', '_')] = value.strip or None

            return meta_infos
        return None

    def parse_command(self, message):
        if self._is_command(message):
            command = message.lstrip('!').strip()
            return command.split()
        return None

    @property
    def is_command(self):
        return self._is_command(self.message)

    def _is_command(self, message):
        if isinstance(message, str) and message.startswith('!'):
            return True
        return False


class Mode(object):
    pass

