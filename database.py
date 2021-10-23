

import pymongo
import os
from dotenv import load_dotenv
from datetime import datetime
import timeit
import time

from random import choice

load_dotenv()

database_name = "AmashiBot"

client = pymongo.MongoClient(os.getenv("URI"))
db = client.get_database(database_name)

users = db.get_collection("users")
mutes = db.get_collection("mutes")
guilds = db.get_collection("guilds")
history = db.get_collection("history")
embeds = db.get_collection("embeds")
suggests = db.get_collection("suggests")
warns = db.get_collection("warns")
roles = db.get_collection("roles")



class Query:
  guild = lambda guild_id: { "guild_id": guild_id }
  user = lambda user_id, guild_id: { "user_id": user_id, "guild_id": guild_id }



async def get_guild(guild_id: int):
  guild = guilds.find_one(Query.guild(guild_id))
  if not guild:
    guild = guilds.insert_one(
      dict(
        guild_id=guild_id,
        verification_role_id=None,
        dm_log=None,
        welcome_channel=None,
        art_channel=None,
        mute_id=None,
        member_id=None,
        menus=[]
      )
    )
  return guild

async def add_mute(guild_id: int, amount: int, user_id: int, mod_id: int, reason=None):
  return mutes.insert_one(
    dict(
      guild_id=guild_id,
      timestamp=datetime.now(),
      time=amount,
      user_id=user_id,
      mod_id=mod_id,
      reason=reason
    )
  )

async def remove_mute(guild_id: int, user_id: int):
  result = mutes.delete_one(
    dict(
      guild_id=guild_id,
      user_id=user_id
    )
  )
  print(result)
  history.insert_one({
    "type": "mute",
    "data": result
  })

async def get_mutes(guild_id):
  results = mutes.find({ "guild_id": guild_id })

  return results
