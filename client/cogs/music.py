from discord.ext import commands
from client.constants import *
import datetime
from client.util.util import parseDate
import discord
import asyncio
from ctypes.util import find_library

class Music:
    """Commands related to music playback"""
    def __init__(self, bot):
        self.bot = bot
        self.voice = None
        self.player = None
        discord.opus.load_opus(find_library("opus"))

    @commands.command(pass_context=True, no_pm=True)
    async def jointheparty(self, ctx, channelName : str):
        """Joins the voice channel you are in"""
        channel = discord.utils.find(lambda m: m.name == channelName, ctx.message.server.channels)
        if not(channel is None):
            if not(self.voice is None):
                await self.voice.move_to(channel)
            self.voice = await self.bot.join_voice_channel(channel)
                 
		
    @commands.command(no_pm=True)
    async def play(self,link : str):
        if not(self.voice is None):
            self.player = await self.voice.create_ytdl_player(link)
            self.player.start()
        else:
            await self.bot.reply("Connecte moi à un channel d\'abord")

    @commands.command(no_pm=True)
    async def stop(self):
        if not(self.player is None):
            self.player.stop()
            self.player = None

    @commands.command(no_pm=True)
    async def leavetheparty(self):
        """Disconnects the bot from voice chat"""
        if not(self.voice is None):
            await self.voice.disconnect()

def setup(bot):
    n = Music(bot)
    bot.add_cog(n)