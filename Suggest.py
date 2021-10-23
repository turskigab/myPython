import discord
from discord.ext import commands
from discord_components import Interaction, ActionRow, Button, ButtonStyle

from database import suggests
from discord import Embed

emojis = ["✔", "❌"]

class Suggest(commands.Cog):
  def __init__(self, bot):
    self.bot: commands.Bot = bot
    self.suggestion_row = ActionRow(
              Button(label="accept", custom_id="suggest allow",style=ButtonStyle.green),
              Button(label="deny",custom_id="suggest deny",style=ButtonStyle.red)
            )

  async def find_suggests(self, guild_id: int):
    return suggests.find_one({ "guild_id": guild_id })

  @commands.Cog.listener("on_message")
  async def on_message(self, message: discord.Message):
    if message.author.bot is True:
      return
    if isinstance(message.channel, discord.DMChannel):
      return
    if not message.guild:
      return
    suggest = await self.find_suggests(message.guild.id)
    if not suggest:
      return
    else:
      if message.channel.id in [suggest['recieve']]:
        user = await self.bot.fetch_user(message.author.id)
        embed = Embed(
          color=self.bot.color,
          description=message.content,
          title="Suggestion"
        ).set_author(name=message.author.display_name, url=user.avatar_url, icon_url=user.avatar_url)
        embed.set_footer(text=message.author.id, icon_url=user.avatar_url)

        await message.channel.send(
          embed=embed,
          components=[
            self.suggestion_row
          ]
          )
        await message.delete()
      else:
        return

  async def allow_suggestion(self, interaction: Interaction, data: dict):
    embed = Embed(
      **interaction.message.embeds[0].to_dict()
    )

    channel = await self.bot.fetch_channel(data['allow'])

    user_id = interaction.message.embeds[0].footer.text

    await channel.send(
      content=f"<@!{user_id}> Congrats your suggestion has been accepted",
      embed=embed
    )
    await interaction.message.delete()

  async def deny_suggestion(self, interaction: Interaction, data: dict):
    embed = Embed(
      **interaction.message.embeds[0].to_dict()
    )

    channel = await self.bot.fetch_channel(data['deny'])
    user_id = interaction.message.embeds[0].footer.text

    await channel.send(
      content=f"<@!{user_id}> Sorry Your Suggestion has been denied",
      embed=embed
    )
    await interaction.message.delete()

  @commands.Cog.listener("on_button_click")
  async def on_button_click(self, interaction: Interaction):
    cid = interaction.custom_id
    args = cid.split(' ')

    if not interaction.author.guild_permissions.administrator:
      return

    if args[0] == 'suggest':
      suggest = await self.find_suggests(interaction.guild_id)
      if args[1] == 'allow':
        print('allowed')
        await self.allow_suggestion(interaction, suggest)
      if args[1] == 'deny':
        print('denied')
        await self.deny_suggestion(interaction, suggest)


  @commands.group()
  async def suggest(self, ctx):
    pass

  async def get_guild_channels(self, guild: discord.Guild) -> list[int]:
    return [c.id for c in guild.channels]

  @suggest.command()
  async def setup(self, ctx: commands.Context, allow: discord.TextChannel, deny: discord.TextChannel, recieve: discord.TextChannel):
    channel_ids = await self.get_guild_channels(ctx.guild)
    if allow.id not in channel_ids:
      await ctx.send("channel doesn't exist in this guild")
    elif deny.id not in channel_ids:
      await ctx.send("channel doesn't exist in this guild")
    elif recieve.id not in channel_ids:
      await ctx.send("channel doesn't exist in this guild")
    else:
      sg = suggests.find_one({ "guild_id": ctx.guild.id })
      if not sg:
        suggests.insert_one({
          "guild_id": ctx.guild.id,
          "allow": allow.id,
          "deny": deny.id,
          "recieve": recieve.id
        })
      else:
        suggests.update_one({ "guild_id": ctx.guild.id }, {
          "$set": {
            "allow": allow.id,
            "deny": deny.id,
            "recieve": recieve.id
          }
        })
      await ctx.send(content="Done!")

  @suggest.command()
  @commands.guild_only()
  @commands.has_guild_permissions(administrator=True)
  async def unsetup(self, ctx: commands.Context):
    suggests.delete_one({ "guild_id": ctx.guild.id })
    await ctx.send(
      content="done",
      delete_after=5
    )


def setup(bot):
  bot.add_cog(Suggest(bot))
