import discord
from discord.ext import commands
from settings import DISCORD_API_SECRET

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print("Online")
    await bot.load_extension('cmds.basic')
    await bot.load_extension('cmds.thread')

    await bot.tree.sync()


if __name__ == '__main__':
    bot.run(DISCORD_API_SECRET)
