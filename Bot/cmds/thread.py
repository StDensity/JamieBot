import discord
from discord.ext import commands


class Thread(commands.Cog):

    @commands.command(name="get_threads", description='Used to get all the threads in a specific channel.')
    async def get_threads(self, ctx, channel_id: int):

        channel = ctx.bot.get_channel(channel_id)

        threads = channel.threads
        tags = []
        titles = []
        for thread in threads:
            tags.append([tags.name for tags in thread.applied_tags])
            titles.append(thread)
        embed_threads = discord.Embed(colour=discord.Colour.dark_teal())
        for index, (title, tag) in enumerate(zip(titles, tags), start=1):
            embed_threads.add_field(name=f"{index:03d} {title}", value=f"Tags: {tag}", inline=False)

        await ctx.send(embed=embed_threads)


async def setup(bot):
    await bot.add_cog(Thread(bot))
