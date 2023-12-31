from discord.ext import commands


class Basic(commands.Cog):

    @commands.hybrid_command(name="hi")
    async def hi(self, ctx):
        await ctx.send("Hiz " + (ctx.author.nick if ctx.author.nick else ctx.author.name))

async def setup(bot):
    await bot.add_cog(Basic(bot))