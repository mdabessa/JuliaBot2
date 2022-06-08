from time import time
from discord.ext import commands
from discord import Message


class Core(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    
    async def _prefix(self, message: Message):
        prefix = await self.bot.get_prefix(message)
        await message.channel.send(f"O prefixo do servidor é: `{prefix}`")


    @commands.command(
        name='ping',
        brief='Pong!',
        description='Um comando para calcular a latencia das mensagens.',
        aliases=['latency', 'latencia']
    )
    async def ping(self, ctx: commands.Context):
        t = time()
        msg = await ctx.send('Ping!')
        t = int((time() - t) * 1000)
        await msg.edit(content=f"`{t}ms` Pong!")


    @commands.command(
        name='prefix',
        brief='Retorna o prefix do bot no servidor.',
        aliases=['prefixo']
    )
    async def prefix(self, ctx: commands.Context):
        await self._prefix(ctx.message)


    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.content == self.bot.user.mention:
            await self._prefix(message)


def setup(bot: commands.Bot):
    bot.add_cog(Core(bot))
