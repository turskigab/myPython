import discord
from discord import message
from discord.embeds import Embed
from discord.ext import commands
from anime_images_api import Anime_Images

from database import Query, get_guild, guilds

anime = Anime_Images()


class Misc(commands.Cog):
  def __init__(self, bot):
    self.bot: commands.Bot = bot

  @commands.command()
  async def avatar(self, ctx: commands.Context, member: discord.Member):
    if not member:
      await ctx.send("Missing Member Mention")
    else:
      embed = discord.Embed(
        title=f"{member.user}'s Avatar",
        url=member.user.avatar_url,
        color=self.bot.color
      ).set_image(member.user.avatar_url)

      await ctx.send(embed=embed)

  @commands.command()
  async def slap(self, ctx: commands.Context, member: discord.Member):
    url = anime.get_sfw("slap")

    embed = discord.Embed(
      title=f"{ctx.author.display_name} slaps {member.display_name}",
      url=url,
      color=self.bot.color
    ).set_image(url=url)

    await ctx.send(embed=embed)

  @commands.command()
  async def kill(self, ctx):
    url = anime.get_sfw("kill")

    embed = discord.Embed(
      title="kill",
      url=url,
      color=self.bot.color
    ).set_image(url=url)

    await ctx.send(embed=embed)

  @commands.command()
  async def kiss(self, ctx: commands.Context, member: discord.Member):
    url = anime.get_sfw("kiss")

    embed = discord.Embed(
      title=f"{ctx.author.display_name} kisses {member.display_name}",
      url=url,
      color=self.bot.color
    ).set_image(url=url)

    await ctx.send(embed=embed)

  @commands.command(name="hug")
  async def hug(self, ctx, target: discord.Member):
    url = anime.get_sfw("hug")

    embed = discord.Embed(
      title=f"{ctx.author.display_name} hugs {target.display_name}!! don't squeeze too hard!",
      url=url,
      color=self.bot.color
    ).set_image(url=url)

    await ctx.send(embed=embed)

  @commands.command()
  async def avatar(self, ctx: commands.Context, user: discord.User):
    embed = discord.Embed(
      title=f"{user}'s Avatar",
      url=user.avatar_url,
      color=self.bot.color
    ).set_image(url=user.avatar_url)

    await ctx.send(
      embed=embed
    )

  @commands.command(
    name="server"
  )
  async def server(self, ctx: commands.Context):
    guild: discord.Guild = ctx.guild
    embed = Embed(
      title="Guild Info",
      description=f"**Members**: {guild.member_count}\n**Channels**: {len(guild.channels)}\n**Roles**: {len(guild.roles)}\n**Emojis**: {len(guild.emojis)}",
      color=self.bot.color
    )

    await ctx.send(
      embed=embed
    )

  @commands.group(
    name="art"
  )
  async def art(self, ctx):
    pass

  @art.command()
  async def setchannel(self, ctx: commands.Context, channel: discord.TextChannel):
    db_guild = await get_guild(ctx.guild.id)

    guilds.update_one(Query.guild(ctx.guild.id), {
      "$set": {
        "art_channel": channel.id
      }
    })
    await ctx.send(
      content="done",
      delete_after=5.0
    )

  @art.command(
    name="submit"
  )
  @commands.dm_only()
  async def submit(self, ctx: commands.Context, guild_id: int):
    msg: discord.Message = ctx.message

    guild = await self.bot.fetch_guild(guild_id)
    if guild is None:
      await ctx.send("could not find guild")

    db_guild = await get_guild(guild_id)

    if not db_guild['art_channel']:
      await ctx.send("guild doesnt have an art channel set up yet")
      return

    channel = await self.bot.fetch_channel(db_guild['art_channel'])

    for attach in msg.attachments:
      await channel.send(
        embed=Embed(
          title="Art",
          url=attach.url,
          color=self.bot.color
        ).set_image(url=attach.url).set_author(name=ctx.author.name, url=ctx.author.avatar_url, icon_url=ctx.author.avatar_url)
      )


def setup(bot):
  bot.add_cog(Misc(bot))
