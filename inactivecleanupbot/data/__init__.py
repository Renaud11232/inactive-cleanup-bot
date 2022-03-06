import os
from .guild import GuildData
import shutil


class Data:

    def __init__(self, data_path, defaults):
        self.__data_path = data_path
        self.__defaults = defaults
        self.__guilds = dict()

    def get_guild_data(self, guild_id):
        guild_id = str(guild_id)
        if guild_id in self.__guilds:
            return self.__guilds[guild_id]
        guild_data_path = os.path.join(self.__data_path, guild_id)
        if not os.path.exists(guild_data_path):
            os.makedirs(guild_data_path)
        guild_data = GuildData(guild_data_path, self.__defaults)
        self.__guilds[guild_id] = guild_data
        return guild_data

    def remove_guild_data(self, guild_id):
        guild_id = str(guild_id)
        self.__guilds.pop(guild_id, None)
        guild_data_path = os.path.join(self.__data_path, guild_id)
        if os.path.exists(guild_data_path):
            shutil.rmtree(guild_data_path)
