import os
import json
import logging
import datetime

import discord
from discord.ext import commands

if "cogs" in __name__:
    from .data.appeals import save_data, remove_data, check_appeal, get_all_appeals, get_judge, save_msg_time, get_msg_time
else:
    from data.appeals import save_data, remove_data, check_appeal, get_all_appeals, get_judge, save_msg_time, get_msg_time

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

        await remove_data(ctx.author.id, ctx.channel_id) # Удаляем данные из json

        await ctx.respond(f"Обжалование было закрыто судьёй <@{ctx.author.id}>")
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if (message.author.id == self.bot.user.id): return

        try:
            appeals = await get_all_appeals()

            for appeal_id in appeals:
                channel = self.bot.get_channel(appeal_id)
                author = await get_judge(appeal_id)

                if (author == True):
                    return

                last_message_time = ""

                async for message in channel.history(limit=None):
                    if (message.author.id == int(author)):
                        last_message_time = message.created_at
                        break
                
                now = datetime.datetime.now()
                form_last_message_time = last_message_time.strftime('%Y-%m-%d %H:%M:%S.%f')
                form_last_message_time = datetime.datetime.fromisoformat(form_last_message_time)

                time_difference = now - form_last_message_time  # Разница во времени
                days = time_difference.seconds  # Получаем количество дней

                if (days >= 1):
                    channel = self.bot.get_channel(appeal_id)
                    await channel.send(f"Пинг судьи <@{author}> (Не было сообщений от судьи более 3-ёх дней)")

        except Exception as e:
            logging.error(e)