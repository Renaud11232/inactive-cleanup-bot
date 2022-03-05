import json
import logging
import sys
import typing

import nextcord
from nextcord.ext import commands
from .data import Data


class InactiveCleanupBot:

    def __init__(self, config_path):
        self.__init_logger()
        self.__logger.info("Loading global configuration file...")
        with open(config_path, "r") as config_file:
            self.__config = json.load(config_file)
        self.__data = Data(self.__config["data"], self.__config["defaults"])
        self.__logger.info("Initializing bot instance...")
        bot = commands.Bot(command_prefix=self.__config["command_prefix"])
        self.__init_bot(bot)
        self.__bot = bot

    def __init_logger(self):
        self.__logger = logging.getLogger("inactivecleanupbot")
        self.__logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.__logger.addHandler(handler)

    def run(self):
        self.__logger.info("Starting bot...")
        self.__bot.run(self.__config["token"])

    def __init_bot(self, bot):

        def is_authorized():
            async def predicate(ctx):
                if await bot.is_owner(ctx.author):
                    self.__logger.debug(f"{ctx.author.name} is the owner of the bot, authorized")
                    return True
                config = self.__data.get_guild_data(ctx.guild.id).get_config()
                if ctx.author.id in config.get_admin_users():
                    self.__logger.debug(f"{ctx.author.name} is in the admin list, authorized")
                    return True
                admin_roles = config.get_admin_roles()
                if any(role.id in admin_roles for role in ctx.author.roles):
                    self.__logger.debug(f"{ctx.author.name} has an admin role, authorized")
                    return True
                self.__logger.debug(f"{ctx.author.name} is not authorized to perform this action")
                return False
            return commands.check(predicate)

        @bot.event
        async def on_ready():
            self.__logger.info("Bot is ready !")

        @bot.check
        async def block_dms(ctx):
            return ctx.guild is not None

        @bot.command(name="set-timeout")
        @is_authorized()
        async def set_timeout(ctx, arg):
            self.__data.get_guild_data(ctx.guild.id).get_config().set_timeout(int(arg))
            await ctx.send(f"Timeout set to {arg}")

        @bot.command(name="add-admin")
        @is_authorized()
        async def add_admin(ctx, admin: typing.Union[nextcord.Role, nextcord.User]):
            config = self.__data.get_guild_data(ctx.guild.id).get_config()
            if isinstance(admin, nextcord.Role):
                config.add_admin_role(admin.id)
                await ctx.send(f"Members of {admin.name} can now configure this bot")
            else:
                config.add_admin_user(admin.id)
                await ctx.send(f"{admin.name} can now configure this bot")

        @bot.command(name="del-admin")
        @is_authorized()
        async def del_admin(ctx, admin: typing.Union[nextcord.Role, nextcord.User]):
            config = self.__data.get_guild_data(ctx.guild.id).get_config()
            if isinstance(admin, nextcord.Role):
                config.remove_admin_role(admin.id)
                await ctx.send(f"Members of {admin.name} can no longer configure this bot")
            else:
                config.remove_admin_user(admin.id)
                await ctx.send(f"{admin.name} can no longer configure this bot")

        @bot.command(name="add-immunity")
        @is_authorized()
        async def add_immunity(ctx, immunity: typing.Union[nextcord.Role, nextcord.User]):
            config = self.__data.get_guild_data(ctx.guild.id).get_config()
            if isinstance(immunity, nextcord.Role):
                config.add_immunity_role(immunity.id)
                await ctx.send(f"Gave immunity to the members of {immunity.name}")
            else:
                config.add_immunity_user(immunity.id)
                await ctx.send(f"Gave immunity to the user {immunity.name}")

        @bot.command(name="del-immunity")
        @is_authorized()
        async def del_immunity(ctx, immunity: typing.Union[nextcord.Role, nextcord.User]):
            config = self.__data.get_guild_data(ctx.guild.id).get_config()
            if isinstance(immunity, nextcord.Role):
                config.remove_immunity_role(immunity.id)
                await ctx.send(f"Members of {immunity.name} are no longer immune")
            else:
                config.remove_immunity_user(immunity.id)
                await ctx.send(f"{immunity.name} is no longer immune")
