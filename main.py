import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from discord_components import ComponentsBot
load_dotenv()

prefix = '.'

class MyHelpCommand(commands.MinimalHelpCommand):
  async def send_pages(self):
    destination = self.get_destination()
    e = discord.Embed(color=bot.color, description='')
    for page in self.paginator.pages:
        e.description += page
    await destination.send(embed=e)

class Bot(ComponentsBot, commands.Bot,):
  def __init__(self, command_prefix, help_command=MyHelpCommand(), description=None, **options):
    super(Bot, self).__init__(command_prefix, help_command=help_command, description=description, **options)

bot = Bot(command_prefix=prefix)

bot.color = discord.Color.from_rgb(0, 200, 200)

@bot.event
async def on_ready():
  print(f"{bot.user} has logged in!")


for cog in [f"cogs.{filename[:-3]}" for filename in os.listdir('./cogs/') if filename.endswith(".py")]:
  try:
    print(f'loading extension {cog}')
    bot.load_extension(cog)
  except Exception as err:
    print(err)

bot.run(os.getenv("TOKEN"))
