import json
import logging
import sys

from nextcord.ext import commands
from .data import Data


class InactiveCleanupBot:

    def __init__(self, config_path):
        self.__init_logger()
        self.__logger.info("Loading configuration file...")
        with open(config_path, "r") as config_file:
            self.__config = json.load(config_file)
        self.__data = Data(self.__config["data"])
        self.__logger.info("Initializing bot instance...")
        bot = commands.Bot(command_prefix=self.__config["command_prefix"])
        self.__init_bot(bot)
        self.__bot = bot

    def __init_logger(self):
        self.__logger = logging.getLogger("inactivecleanupbot")
        self.__logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.__logger.addHandler(handler)

    def run(self):
        self.__logger.info("Starting bot...")
        self.__bot.run(self.__config["token"])

    def __init_bot(self, bot):

            @bot.event
            async def on_ready():
                self.__logger.info("Bot is ready !")

            @bot.command(pass_context=True)
            async def test(ctx):
                self.__logger.info("Got command !")

