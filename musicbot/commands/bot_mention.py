import discord
from discord.ext import commands

class BotMentionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if self.bot.user in message.mentions:
            await message.channel.send(
                f"{message.author.mention} Salut ! Je suis le bot de musique. "
                "Tape `/music` pour lancer la rotation aléatoire, `/yt` pour jouer une vidéo, ou `/help` pour voir toutes mes commandes !"
            )

async def setup(bot):
    await bot.add_cog(BotMentionCog(bot))

