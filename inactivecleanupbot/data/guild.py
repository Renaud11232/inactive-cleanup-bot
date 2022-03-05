from .config import GuildConfig
from .user import GuildUsers


class GuildData:

    def __init__(self, path, defaults):
        self.__config = GuildConfig(path, defaults)
        self.__users = GuildUsers(path)

    def get_config(self):
        return self.__config

    def get_users(self):
        return self.__users
