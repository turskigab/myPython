import discord
from discord.channel import TextChannel
from discord.embeds import Embed
from discord.ext import commands

from database import Query, get_guild, guilds

class Default(commands.Cog):
  def __init__(self, bot):
    self.bot: commands.Bot = bot

  @commands.command(
    name='whois'
  )
  @commands.guild_only()
  async def whois(self, ctx: commands.Context, member: discord.Member):
    user: discord.User = await self.bot.fetch_user(member.id)



    embed = Embed(
      title=f"Who Is: {member.display_name}",
      description=f"**username**: {user}\n**created_at**: <t:{int(user.created_at.timestamp())}>\n**joined_at**: <t:{int(member.joined_at.timestamp())}>",
      color=self.bot.color,
    ).set_thumbnail(
      url=user.avatar_url
    ).set_author(
      name=user.name,
      url=user.avatar_url,
      icon_url=user.avatar_url
    )


    await ctx.send(embed=embed)

  @commands.Cog.listener()
  async def on_member_join(self, member: discord.Member):
    db_guild = await get_guild(member.guild.id)
    guild = member.guild

    print("member has joined a server")

    if not db_guild['welcome_channel']:
      return
    else:
      channel = await self.bot.fetch_channel(db_guild['welcome_channel'])

      embed = discord.Embed(
        title="Welcome",
        description=f"Welcome <@!{member.id}>",
        color=self.bot.color
      )

      await channel.send(
        embed=embed,
        content=f"Welcome <@!{member.id}>"
      )


  @commands.command()
  async def welcome(self, ctx: commands.Context, channel: discord.TextChannel):
    if not channel:
      await ctx.send(content="Missing Channel Mention")
    elif type(channel) != TextChannel:
      await ctx.send(content="Mentioned channel must be a text channel")
    elif channel.guild.id != ctx.guild.id:
      await ctx.send(content="Channel must Be in this guild")
    else:
      guilds.update_one(Query.guild(ctx.guild.id), {
        "$set": dict(
            welcome_channel = channel.id
          )
      })
      await ctx.send(content=f"set welcome channel to <#{channel.id}>")


  @commands.command()
  async def ping(self, ctx):
    await ctx.send(f"My Ping is: {round(self.bot.latency * 1000)}ms")

def setup(bot):
    bot.add_cog(Default(bot))
