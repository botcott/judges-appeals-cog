import os
import json
import logging
import datetime

import discord
from discord.ext import commands

if "cogs" in __name__:
    from .data.appeals import (save_data, remove_data, check_appeal, get_judge, 
        get_all_appeals, calc_time, update_time, get_time)
else:
    from data.appeals import (save_data, remove_data, check_appeal, get_judge, 
        get_all_appeals, calc_time, update_time, get_time)

with open(f"{os.path.dirname(__file__)}/config/config.json", "r", encoding="utf-8") as f:
    cfg = json.load(f)

appeal_channel_id = int(cfg["appeal_channel_id"])

class JudgesAppealsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @commands.slash_command(name="accept_appeal", description="Принять обжалование")
    async def accept_appeal(self, ctx: discord.ApplicationContext):

        if (not isinstance(ctx.channel, discord.Thread) or ctx.channel.parent_id != appeal_channel_id):
            await ctx.respond("Данная команда работает только в форуме обжалований", ephemeral=True)
            return
        
        if (await check_appeal(ctx.channel_id)):
            await ctx.respond("Данное обжалование уже принято", ephemeral=True)
            return

        await save_data(ctx.author.id, ctx.channel_id) # Записываем данные в json

        await ctx.respond(f"Обжалование принято судьёй <@{ctx.author.id}>")

    @commands.slash_command(name="close_appeal", description="Закрыть обжалование")
    async def close_appeal(self, ctx: discord.ApplicationContext):

        if (not isinstance(ctx.channel, discord.Thread) or ctx.channel.parent_id != appeal_channel_id):
            await ctx.respond("Данная команда работает только в форуме обжалований", ephemeral=True)
            return
        
        if (await check_appeal(ctx.channel_id) == False):
            await ctx.respond("Данное обжалование ещё не принято", ephemeral=True)
            return

        await remove_data(ctx.author.id, ctx.channel_id)
        thread = self.bot.get_channel(ctx.channel_id)
        await ctx.respond(f"Обжалование было закрыто судьёй <@{ctx.author.id}>")

        await thread.edit(archived=True, locked=True)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if (message.author.id == self.bot.user.id): return
        
        all_appeals = await get_all_appeals()
        
        for appeal in all_appeals:
            judge_id = await get_judge(appeal)
            if message.channel.id == appeal:
                if message.author.id == int(judge_id):
                    await update_time(int(judge_id), int(appeal))

            time = await get_time(int(judge_id), int(appeal))
            now = datetime.datetime.now()
            now_time = now.strftime("%m.%Y.%H.%M.%S")

            seconds = await calc_time(time, now_time)

            if seconds >= 10:
                await update_time(int(judge_id), int(appeal))
                channel = self.bot.get_channel(int(appeal))
                await channel.send(f"Пинг судьи <@{int(judge_id)}> (Не было сообщений от судьи более 3-ёх дней)")