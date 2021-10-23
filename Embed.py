
import discord
from discord.embeds import Embed
from discord.ext import commands
from discord_components import ActionRow, Select, SelectOption, Button, ButtonStyle, Interaction
from math import floor

from database import embeds

valid_properties = [
      'title',
      'description'
    ]

class Maker(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  async def get_embed(self, guild_id: int, name: str):
    return embeds.find_one({ "guild_id": guild_id, "name": name})

  @commands.group(
    name="embed",
    help="create, edit, and send embeds"
  )
  async def embed(self, ctx):
    pass

  @embed.command(
    name="create",
    help="[name]"
  )
  async def create(self, ctx: commands.Context, name: str):

    save_data = Embed(
      title="None",
      description="None",
      color=self.bot.color
    ).to_dict()

    embeds.insert_one({
      "guild_id": ctx.guild.id,
      "name": name,
      "data": save_data
    })

    await ctx.send(
      content=f"created new embed save {name}"
    )

  @embed.command(
    name="edit",
    help="[property] [text]",
    description=f"Edits a created embed.\n> Editable Properties: {','.join([f'`{i}`' for i in valid_properties])}"
  )
  async def edit(self, ctx: commands.Context, name: str, property: str, value: str):
    data = await self.get_embed(ctx.guild.id, name)



    if not data:
      await ctx.send("no embed found")
    else:
      if property in valid_properties:
        new_embed = Embed(**data['data'])

        setattr(new_embed, property, value)

        embeds.update_one({ "guild_id": ctx.guild.id, "name": name }, {
          "$set": {
            "data": new_embed.to_dict()
          }
        })
        await ctx.send(content="Done!", delete_after=5.0)
      else:
        await ctx.send(
          content=f"no usable property settable for embed. options: {','.join([f'`{i}`' for i in valid_properties])}"
        )

  @embed.command()
  async def send(self, ctx: commands.Context, name: str):
    data = await self.get_embed(ctx.guild.id, name)

    if not data:
      await ctx.send("no embed with that name exists")
    else:
      await ctx.send(
        embed=Embed(**data['data'])
      )


  @commands.Cog.listener(name="on_button_click")
  async def on_button_click(self, interaction: Interaction):

    if interaction.custom_id.startswith("embed role"):
      args = interaction.custom_id.split("embed role ")
      role_id = args[1]

      print(args)

      role = discord.utils.find(lambda role: role.id == int(role_id), interaction.guild.roles)
      if not role:
        payload = interaction.message

        comp: Button = payload.get_component(interaction.custom_id)
        if not comp:
          return
        else:
          comp.set_disabled(True)

        await interaction.edit_origin(
          embeds=payload.embeds,
          components=payload.components
        )
      else:
        if role.id in [role.id for role in interaction.author.roles]:
          await interaction.author.remove_roles(role)
        else:
          await interaction.author.add_roles(role)
        await interaction.respond(
          content="Done",
          ephemeral=True
        )

  @commands.command()
  async def addbutton(self, ctx: commands.Context, label: str, style: str, role_id: int):
    msg: discord.Message = ctx.message
    if not msg.reference:
      await ctx.send("Missing Message Target. please reply to the message you want to add the button to")
    else:
      ref = await ctx.fetch_message(msg.reference.message_id)

      valid_button_colors = ['red', 'green', 'blue', 'gray']

      if style not in valid_button_colors:
        await ctx.send(f"Invalid button color choosen please choose: {', '.join(valid_button_colors)}")
        return


      rows: list[ActionRow] = []

      components = []
      try:
        components = getattr(ref, 'components')
      except AttributeError:
        pass
      else:
        rows = ref.components
      print("finally")



      print(rows, 'hi')


      new_btn = Button(
          label=label,
          style=getattr(ButtonStyle, style),
          custom_id=f"embed role {role_id}"
        )
      print("added button")

      done = False
      for row in rows:
        if done == True:
          break
        if len(row) < 5:
          done = True
          row.add_component(new_btn)
      if done == False:
        rows.append(
          ActionRow(
            new_btn
          )
        )
        done = True

      new_rows = [
        list(set([Button(label=c._label, style=c._style, custom_id=c.custom_id) for c in row.components])) for row in rows
      ]

      print(new_rows)

      await ctx.send(
        content=ref.content,
        embeds=ref.embeds,
        components=new_rows
      )
      await ref.delete()

def setup(bot):
  bot.add_cog(Maker(bot))






