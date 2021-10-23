import discord
from discord.ext import commands
from discord.ext.commands.errors import (
  ExtensionAlreadyLoaded,
  ExtensionError,
  ExtensionNotLoaded,
  ExtensionNotFound,
  ExtensionFailed
)
import asyncio
import os

devs = [635959963134459904, 827749968848355338]

from database import Query, users

async def is_dev(m: discord.Message):
    return m.author.id in devs

class Dev(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.Cog.listener("on_command_error")
  async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
    txt = str(error)

    if len(txt) > 2000:
      txt = txt[2000:]

    embed = discord.Embed(
      title=str(error.__class__.__name__),
      description=f"```xl\n{txt}\n```",
      color=self.bot.color
    ).add_field(name="Dev Data", value=f"cog: {ctx.cog.__class__.__name__}\ncommand: {ctx.command}"
    )


    await ctx.send(
      embed=embed,
      reference=ctx.message)

  async def send_confirm(self, ctx):
    msg = await ctx.send('done')
    await asyncio.sleep(5)
    await msg.delete()

  @commands.command(
    name="cmd",
    hidden=True
  )
  @commands.check(is_dev)
  async def cmd(self, ctx, *, input_):
    os.system(input_)

  async def reload_extension(self, ctx: commands.Context, extension: str):
    try:
      self.bot.reload_extension(name=extension)
    except ExtensionAlreadyLoaded as err:
      await ctx.send(f"ExtensionAlreadyLoaded: {err}")
    except ExtensionError as err:
      await ctx.send(f"ExtensionError: {err}")
    except ExtensionNotLoaded as err:
      await ctx.send(f"ExtensionNotLoaded: {err}")
    except ExtensionNotFound as err:
      await ctx.send(f"ExtensionNotFound: {err}")
    except ExtensionFailed as err:
      await ctx.send(f"ExtensionFailed: {err}")

  async def load_extension(self, ctx: commands.Context, extension: str):
    try:
      self.bot.load_extension(name=extension)
    except ExtensionAlreadyLoaded as err:
      await ctx.send(f"ExtensionAlreadyLoaded: {err}")
    except ExtensionError as err:
      await ctx.send(f"ExtensionError: {err}")
    except ExtensionNotLoaded as err:
      await ctx.send(f"ExtensionNotLoaded: {err}")
    except ExtensionNotFound as err:
      await ctx.send(f"ExtensionNotFound: {err}")
    except ExtensionFailed as err:
      await ctx.send(f"ExtensionFailed: {err}")

  async def unload_extension(self, ctx: commands.Context, extension: str):
    try:
      self.bot.unload_extension(name=extension)
    except ExtensionAlreadyLoaded as err:
      await ctx.send(f"ExtensionAlreadyLoaded: {err}")
    except ExtensionError as err:
      await ctx.send(f"ExtensionError: {err}")
    except ExtensionNotLoaded as err:
      await ctx.send(f"ExtensionNotLoaded: {err}")
    except ExtensionNotFound as err:
      await ctx.send(f"ExtensionNotFound: {err}")
    except ExtensionFailed as err:
      await ctx.send(f"ExtensionFailed: {err}")

  @commands.group(
    name="cog",
    aliases=["cogs"],
    hidden=True
  )
  async def cog(self, ctx: commands.Context):
    pass

  @cog.command(help="Dev Only", hidden=True)
  @commands.check(is_dev)
  async def load(self, ctx: commands.Context, *, extension: str):
    await self.load_extension(ctx, extension)
    await self.send_confirm(ctx)

  @cog.command(help="Dev Only", hidden=True)
  @commands.check(is_dev)
  async def unload(self, ctx: commands.Context, *, extension: str):
    await self.unload_extension(ctx, extension)
    await self.send_confirm(ctx)

  @cog.command(help="Dev Only", hidden=True)
  @commands.check(is_dev)
  async def reload(self, ctx: commands.Context, *, extension: str):
    await self.unload_extension(ctx, extension)
    await self.load_extension(ctx, extension)
    await self.send_confirm(ctx)

def setup(bot):
    bot.add_cog(Dev(bot))
