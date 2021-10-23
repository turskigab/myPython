from datetime import datetime
import discord
from discord.embeds import Embed
from discord.ext import commands
from discord.ext.commands.errors import MissingPermissions
from discord_components import Button, ButtonStyle, Interaction

from database import Query, get_guild, guilds, users, mutes, warns, roles

class Mod(commands.Cog):
  def __init__(self, bot):
    self.bot: commands.Bot = bot


  @commands.command(
    name="dms"
  )
  @commands.guild_only()
  async def dms(self, ctx: commands.Context, target: discord.User):
    if not target.dm_channel:
      await ctx.send(
        content="No messages have been made with this user"
      )
      return
    channel_id = int(target.dm_channel.id)
    if True:
      txt = ''
      print(target.dm_channel)
      messages = await target.dm_channel.history(limit=100, oldest_first=True).flatten()
      for message in messages:
        txt += f"**{message.author}**: {message.content}\n"

      await ctx.send(
        embed=Embed(
          title="messages",
          description=txt
        )
      )





  @commands.command(description="Mutes the specified user.")
  @commands.has_permissions(manage_messages=True)
  @commands.guild_only()
  async def mute(self, ctx, member: discord.Member, *, reason=None):
    guild: discord.Guild = ctx.guild
    muterole = roles.find_one({ 'guild_id': ctx.guild.id, 'type': 'mute' })

    if not muterole:
      await ctx.send(
        content="no mute role set for this server"
      )
      return


    mutedRole = discord.utils.get(guild.roles, id=muterole['role_id'])

    if not mutedRole:
      mutedRole = await guild.create_role(name="muted", color=discord.Colour.light_gray())

      for channel in guild.channels:
        await channel.set_permissions(mutedRole, speak=False, send_messages=False, read_message_history=True, read_messages=True, manage_messages=False)

    embed = discord.Embed(title="muted", description=f"{member.mention} was muted ", colour=discord.Colour.light_gray())
    embed.add_field(name="reason:", value=reason, inline=False)
    await ctx.send(embed=embed)
    await member.add_roles(mutedRole, reason=reason)
    await member.send(f"you have been muted from: {guild.name} for reason: {reason}")

  @commands.command(description="Unmutes a specified user.")
  @commands.has_permissions(manage_messages=True)
  async def unmute(self, ctx, member: discord.Member):

    muterole = roles.find_one({ 'guild_id': ctx.guild.id, 'type': 'mute' })

    if not muterole:
      await ctx.send(
        content="no mute role set for this server"
      )
      return

    mutedRole = discord.utils.get(ctx.guild.roles, name="muted")

    if not mutedRole:
      mutedRole = await ctx.guild.create_role(name="muted", color=discord.Colour.light_gray())

      for channel in ctx.guild.channels:
        await channel.set_permissions(mutedRole, speak=False, send_messages=False, read_message_history=True, read_messages=False, veiw_channel=True)

    await member.remove_roles(mutedRole)
    await member.send(f"you have unmuted from: {ctx.guild.name}")
    embed = discord.Embed(title="unmute", description=f" unmuted-{member.mention}",colour=discord.Colour.light_gray())
    await ctx.send(embed=embed)


  @commands.command(
    name="ban"
  )
  @commands.guild_only()
  @commands.has_permissions(ban_members=True)
  async def ban(self, ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'User {member} has been kick')

  @commands.command(
    name="unban"
  )
  @commands.guild_only()
  @commands.has_permissions(administrator=True)
  async def unban(self, ctx, *, member):
    banned_users = await ctx.guild.bans()
    vals = member.split("#")
    if len(vals) != 2:
      await ctx.send(f"Invalid Tag. `Example: {self.bot.user}`")
      return
    member_name, member_discriminator = vals

    found = False

    for ban_entry in banned_users:
      user = ban_entry.user

      if (user.name, user.discriminator) == (member_name, member_discriminator):
        found = True
        await ctx.guild.unban(user)
        await ctx.send(f'Unbanned {user.mention}')
        break

    if not found:
      await ctx.send(content=f"Could not find user with that tag. `Example Tag: {self.bot.user}`")

  @commands.command(name='kick')
  @commands.has_permissions(kick_members=True)
  async def kick(self, ctx, member: discord.Member, *, reason=None):
      await member.kick(reason=reason)
      await ctx.send(f'User {member} has been kick')

  @commands.command(
    name="nickname"
  )
  @commands.guild_only()
  async def nickname(self, ctx: commands.Context, name: str):
    member: discord.Member = ctx.author
    try:
      await member.edit(nick=name)
    except Exception as err:
      print(err)
      if isinstance(err, MissingPermissions):
        await ctx.send(f"Missing Permissions.\n> Error:\n{err}")
      else:
        await ctx.send(content="There was an error setting your nickname")
    else:
      await ctx.send(content="Done!")

  async def get_user_history(self, guild_id: int, member_id: int):
    user_warns = warns.find({ "guild_id": guild_id, "user_id": member_id })
    user_mutes = mutes.find({ "guild_id": guild_id, "user_id": member_id })
    return user_warns, user_mutes

  @commands.command()
  @commands.guild_only()
  @commands.has_guild_permissions(administrator=True)
  async def checkwarns(self, ctx: commands.Context, member: discord.Member):
    user_warns, user_mutes = await self.get_user_history(ctx.guild.id, member.id)
    txt = ''

    x = 1
    for i in user_warns:
      txt += f"**{x}**: {i['reason']} (`{i['_id']}`)"
      x += 1

    embed = Embed(
      title="warns",
      description=txt
    )

    await ctx.send(
      embed=embed,
      reference=ctx.message
    )

    @commands.command(
      name="warn"
    )
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def warn(self, ctx: commands.Context, target: discord.Member, *, reason: str):
      now = datetime.now()
      res = warns.insert_one({
        "user_id": target.id,
        'guild_id': ctx.guild.id,
        "mod_id": ctx.author.id,
        "reason": reason,
        "date": datetime(now).date(),
      })

      await ctx.send(
        content=f"<@!{target.id}> has been warned!\nID: `{res.inserted_id}`\n"
      )

  @commands.command(
    name="unwarn"
  )
  @commands.guild_only()
  @commands.has_guild_permissions(administrator=True)
  async def unwarn(self, ctx: commands.Context, target: discord.Member, id: str):
    res = warns.delete_one({ 'user_id': target.id, "_id": id })
    await ctx.send("done")

  @commands.command(
    name='warn'
  )
  @commands.guild_only()
  @commands.has_guild_permissions(administrator=True)
  async def warn(self, ctx: commands.Context, target: discord.Member, *, reason: str):
    warns.insert_one({
      'user_id': target.id,
      'guild_id': ctx.guild.id,
      'mod_id': ctx.author.id,
      'reason': reason
    })

    await ctx.send(
      content=f"<@!{target.id}> has been warned."
    )

  @commands.command()
  @commands.guild_only()
  @commands.has_guild_permissions(administrator=True)
  async def setmuterole(self, ctx: commands.Context, muterole: discord.Role):
    role = roles.find_one({ 'guild_id': ctx.guild.id, "type": "mute" })

    if not role:
      roles.insert_one({
        "guild_id": ctx.guild.id,
        'role_id': muterole.id,
        'type': "mute"
      })
    else:
      roles.delete_one({ 'guild_id': ctx.guild.id, "type": "mute" })
      roles.insert_one({
        "guild_id": ctx.guild.id,
        'role_id': muterole.id,
        'type': "mute"
      })

    await ctx.send(
      content="done",
      delete_after=5
    )


def setup(bot):
  bot.add_cog(Mod(bot))
