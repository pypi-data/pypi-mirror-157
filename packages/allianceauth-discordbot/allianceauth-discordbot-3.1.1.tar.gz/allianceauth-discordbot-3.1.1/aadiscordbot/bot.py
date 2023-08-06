import logging
import sys
import time
import traceback
from aadiscordbot import app_settings
import aiohttp
import aioredis
import pendulum

from .cogs.utils import context
from . import bot_tasks
from aadiscordbot.app_settings import DISCORD_BOT_ACCESS_DENIED_REACT, DISCORD_BOT_MESSAGE_INTENT, DISCORD_BOT_PREFIX

import discord
from discord.ext import commands, tasks

import django
from django.conf import settings
import django.db

from allianceauth import hooks
from kombu import Connection, Queue, Consumer
from socket import timeout

import aadiscordbot


description = """
AuthBot is watching...
"""

logger = logging.getLogger(__name__)

INVITE_URL = f"https://discord.com/api/oauth2/authorize?client_id={settings.DISCORD_APP_ID}&permissions=8&scope=bot%20applications.commands"

queuename = "aadiscordbot"
queue_keys = [f"{queuename}",
              f"{queuename}\x06\x161",
              f"{queuename}\x06\x162",
              f"{queuename}\x06\x163",
              f"{queuename}\x06\x164",
              f"{queuename}\x06\x165",
              f"{queuename}\x06\x166",
              f"{queuename}\x06\x167",
              f"{queuename}\x06\x168",
              f"{queuename}\x06\x169"]


class AuthBot(commands.Bot):
    def __init__(self):
        django.setup()
        client_id = settings.DISCORD_APP_ID
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = app_settings.DISCORD_BOT_MESSAGE_INTENT

        super().__init__(
            command_prefix=DISCORD_BOT_PREFIX,
            description=description,
            intents=intents,
        )
        print(f"Authbot Started with command prefix {DISCORD_BOT_PREFIX}")

        self.redis = None
        self.redis = self.loop.run_until_complete(aioredis.create_pool(getattr(
            settings, "BROKER_URL", "redis://localhost:6379/0"), minsize=5, maxsize=10))
        print('redis pool started', self.redis)
        self.client_id = client_id
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.tasks = []

        self.message_connection = Connection(
            getattr(settings, "BROKER_URL", 'redis://localhost:6379/0'))
        queues = []
        for que in queue_keys:
            queues.append(Queue(que))
        self.message_consumer = Consumer(self.message_connection, queues, callbacks=[
                                         self.on_queue_message], accept=['json'])
        self.cog_names_loaded = []
        self.cog_names_failed = []
        for hook in hooks.get_hooks("discord_cogs_hook"):
            for cog in hook():
                try:
                    self.load_extension(cog)
                    self.cog_names_loaded.append(cog)
                except Exception as e:
                    logger.exception(f"Failed to load cog {cog}")
                    self.cog_names_failed.append(cog)

    def on_queue_message(self, body, message):
        print('RECEIVED MESSAGE: {0!r}'.format(body))
        try:
            task_headers = message.headers
            _args = body[0]
            _kwargs = body[1]

            if 'aadiscordbot.tasks.' in task_headers["task"]:
                task = task_headers["task"].replace("aadiscordbot.tasks.", '')
                task_function = getattr(bot_tasks, task, False)
                if task_function:
                    self.tasks.append((task_function, _args, _kwargs))
                    if not bot_tasks.run_tasks.is_running():
                        bot_tasks.run_tasks.start(self)
                else:
                    logger.debug("No bot_task for that auth_task?")
            else:
                logger.debug("i got an invalid auth_task")

        except Exception as e:
            logger.error("Queue Consumer Failed")
            logger.error(e, exc_info=1)
        message.ack()

    async def on_ready(self):
        if not hasattr(self, "currentuptime"):
            self.currentuptime = pendulum.now(tz="UTC")
        activity = discord.Activity(name="Everything!",
                                    application_id=0,
                                    type=discord.ActivityType.watching,
                                    state="Monitoring",
                                    details="Waiting for Shenanigans!",
                                    emoji={"name": ":smiling_imp:"}
                                    )
        await self.change_presence(activity=activity)

        self.poll_queue.start()
        logger.info("Ready")

    async def process_commands(self, message):
        ctx = await self.get_context(message)
        if ctx.command is None:
            return
        django.db.close_old_connections()
        await self.invoke(ctx)
        django.db.close_old_connections()

    async def on_interaction(self, interaction):
        django.db.close_old_connections()
        await self.process_application_commands(interaction)
        django.db.close_old_connections()

    async def on_message(self, message):
        if message.author.bot:
            return
        await self.process_commands(message)

    async def sync_commands(self, *args, **kwargs):
        try:
            return await super(__class__, self).sync_commands(*args, **kwargs)
        except discord.Forbidden:
            logger.error(
                "******************************************************")
            logger.error("|   AuthBot was Unable to Sync Slash Commands!!!!")
            logger.error(
                "|   Please ensure your bot was invited to the server with the correct scopes")
            logger.error("|")
            logger.error("|   To redo your scopes,")
            logger.error("|      1. Refresh Scopes with this link:")
            logger.error(f"|        {INVITE_URL}   ")
            logger.error(
                "|      2. Move the bots role to top of the roles tree if its not there already")
            logger.error("|      3. Restart Bot")
            logger.error(
                "******************************************************")

    @tasks.loop(seconds=1.0)
    async def poll_queue(self):
        message_avail = True
        while message_avail:
            try:
                with self.message_consumer:
                    self.message_connection.drain_events(timeout=0.01)
            except timeout as e:
                # logging.exception(e)
                message_avail = False

    async def on_resumed(self):
        print("Resumed...")

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            print(error)
            await ctx.send(error)
        elif isinstance(error, commands.MissingRequiredArgument):
            print(error)
            await ctx.send(error)
        elif isinstance(error, commands.NoPrivateMessage):
            print(error)
            await ctx.send(error)
        elif isinstance(error, commands.CommandInvokeError):
            print(error)
            return await ctx.send(error)
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(
                "Sorry, I don't have the required permissions to do that here:\n{0}".format(
                    error.missing_perms)
            )
        elif isinstance(error, commands.MissingPermissions):
            await ctx.message.add_reaction(chr(DISCORD_BOT_ACCESS_DENIED_REACT))
            await ctx.message.reply("Sorry, you do not have permission to do that here.")
        elif isinstance(error, commands.NotOwner):
            print(error)
            await ctx.send(error)
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.message.add_reaction(chr(0x274C))

    def run(self):
        # self.load_extension("aadiscordbot.slash.admin")
        try:

            logger.info(
                "******************************************************")
            logger.info(f"         ##            Alliance Auth 'AuthBot'")
            logger.info(
                f"        ####           Version         :  {aadiscordbot.__version__}")
            logger.info(
                f"       #######         Branch          :  {aadiscordbot.__branch__}")
            logger.info(
                f"      #########        Message Intents :  {app_settings.DISCORD_BOT_MESSAGE_INTENT}")
            logger.info(
                f"     ######## ((       Prefix          :  {app_settings.DISCORD_BOT_PREFIX}")
            logger.info(
                f"    ###### ((((((      Bot Join Link   :  {INVITE_URL}")
            logger.info(f"   ###        ((((     Starting up...")
            logger.info(f"  ##             ((")
            logger.info(f"                       [Cogs Loaded]")
            for c in self.cog_names_loaded:
                logger.info(f"                         - {c}")
            if len(self.cog_names_failed):
                logger.info(f"                       [Cog Failures]")
                for c in self.cog_names_failed:
                    logger.info(f"                         - {c}")
            logger.info(
                "******************************************************")
            super().run(settings.DISCORD_BOT_TOKEN, reconnect=True)
        except discord.PrivilegedIntentsRequired as e:
            logger.error("Unable to start bot with Messages Intent! Going to Sleep for 2min. "
                         "Please enable the Message Intent for your bot. "
                         "https://support-dev.discord.com/hc/en-us/articles/4404772028055"
                         f"{e}", exc_info=False)
            logger.info("If you wish to run without the Message Intent disable it in the local.py. "
                        "DISCORD_BOT_MESSAGE_INTENT=False", exc_info=False)
            time.sleep(120)
        except Exception as e:
            logger.error("Unable to start bot! going to sleep for 2 min. "
                         f"{e}", exc_info=True)
            time.sleep(120)
