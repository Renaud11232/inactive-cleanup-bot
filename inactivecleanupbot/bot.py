import json
import logging
import sys
import typing

import nextcord
from nextcord.ext import commands, tasks
from .data import Data


class InactiveCleanupBot:

    def __init__(self, config_path):
        self.__init_logger()
        self.__logger.info("Loading global configuration file...")
        with open(config_path, "r") as config_file:
            self.__config = json.load(config_file)
        self.__data = Data(self.__config["data"], self.__config["defaults"])
        self.__logger.info("Initializing bot instance...")
        intents = nextcord.Intents.default()
        intents.members = True
        intents.messages = True
        bot = commands.Bot(command_prefix=self.__config["command_prefix"], intents=intents)
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
            self.__logger.info("Bot is ready, refreshing user lists...")
            for guild in bot.guilds:
                self.__data.get_guild_data(guild.id).get_users().track_new_members(guild.members)
            self.__logger.info("Finished refreshing user lists...")
            self.__logger.info("Starting background task...")
            background_task.start()

        @bot.event
        async def on_message(message: nextcord.Message):
            if message.guild:
                self.__logger.debug(f"Recieved message from {message.author.name}, updating activity")
                self.__data.get_guild_data(message.guild.id).get_users().update_member(message.author)
            await bot.process_commands(message)

        @bot.event
        async def on_member_join(member: nextcord.Member):
            self.__logger.debug(f"{member.name} joined a guild, updating activity")
            self.__data.get_guild_data(member.guild.id).get_users().update_member(member)

        @bot.event
        async def on_voice_state_update(member: nextcord.Member, before: nextcord.VoiceState, after: nextcord.VoiceState):
            self.__logger.debug(f"{member.name} changed voice state, updating activity")
            self.__data.get_guild_data(member.guild.id).get_users().update_member(member)

        @bot.event
        async def on_guild_join(guild: nextcord.Guild):
            self.__logger.debug("The bot joined a new guild, updating user list")
            self.__data.get_guild_data(guild.id).get_users().track_new_members(guild.members)

        @bot.event
        async def on_error(event, *args, **kwargs):
            self.__logger.error(event)

        @bot.check
        async def block_dms(ctx):
            return ctx.guild is not None

        @bot.command(name="set-timeout")
        @is_authorized()
        async def set_timeout(ctx, timeout: int):
            self.__data.get_guild_data(ctx.guild.id).get_config().set_timeout(timeout)
            await ctx.send(f"Timeout set to {timeout}")

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

        @bot.command(name="set-active")
        @is_authorized()
        async def set_active(ctx, active: bool):
            self.__data.get_guild_data(ctx.guild.id).get_config().set_active(active)
            await ctx.send(f"Set active to {active}")

        @tasks.loop(minutes=1.0)
        async def background_task():
            for guild in bot.guilds:
                self.__logger.debug(f"Finding inactive members for guild {guild.name}")
                inactive_users = self.__data.get_guild_data(guild.id).get_users().inactive()
                for inactive_user in inactive_users:
                    member = guild.get_member(inactive_user)
                    self.__logger.debug(f"{member.name} is inactive and is candidate to be kicked")
                    immune_by_role = any(role.id in self.__data.get_guild_data(guild.id).get_config().get_immunity_roles() for role in member.roles)
                    immune_by_user = member.id in self.__data.get_guild_data(guild.id).get_config().get_immunity_users()
                    if member.bot:
                        self.__logger.debug(f"{member.name} is a bot and will not be kicked")
                    elif immune_by_role or immune_by_user:
                        self.__logger.debug(f"{member.name} is immune and cannot be kicked")
                    elif self.__data.get_guild_data(guild.id).get_config().is_active():
                        self.__logger.info(f"kicking {member.name} from the guild")
                        await guild.kick(guild.get_member(inactive_user))
                    else:
                        self.__logger.debug(f"Not kicking {member.name} because the bot is set to inactive")
                self.__logger.debug(f"Done looking for inactive users in {guild.name}")
