import discord
import os
import asyncio
from discord.ext import commands
from src import music
from src import nba
from src import misc
from replit import db
from keep_alive import keep_alive

def get_prefix(client, message): 
  id = str(message.guild.id)
  try:
    return db["guild_symbols"][id]
  except:
    db["guild_symbols"][id] = "$"
    return db["guild_symbols"][id]

client = commands.Bot(command_prefix=get_prefix, intents=discord.Intents().all())
cogs = [music, nba, misc]

async def cogs_start():
  for i in range(len(cogs)):
    await cogs[i].setup(client)
    
async def main():
  await cogs_start()
  # keep_alive()
  await client.start(os.environ["token"])

#-----Load database
if "guild_symbols" not in db.keys():
  db["guild_symbols"] = {}

if "responding" not in db.keys():
  db["responding"] = True

if "quotes" not in db.keys():
  db["quotes"] = []

if "symbol_list" not in db.keys():
  db["symbol_list"] = ["`", "~", "!", "$", "%", "^", "&", "*", "<", ">", "?", "."]

if "symbols" not in db.keys():
  symbols = ""
  symbol_list = db["symbol_list"]   
   
  for i in range(len(symbol_list)):
    if i == len(symbol_list) - 1:
      symbols += symbol_list[i]
    else:
      symbols += symbol_list[i] + ",  "

  db["symbols"] = symbols

if "info" not in db.keys():
  info = [[[]], [[]], [[]]]
  info[0].insert(0, "General:")
  info[1].insert(0, "Music:")
  info[2].insert(0, "NBA:")

  info[0][1].append("[changeprefix, changesymbol, changecommand] <prefix> - Changes the prefix symbol for the bot. (Admin only)")
  info[0][1].append("cp3 - Rolls a random video about Chris Paul.")
  info[0][1].append("allcp3 - Shows the full list of Chris Paul videos.")
  info[0][1].append("[highlights, hl, hls] - Rolls a random NBA highlight video.")
  info[0][1].append("[allhighlights, allhl, allhls] - Shows the full list of NBA highlights.")
  
  info[1][1].append("Makes the bot join the voice channel you're in.")
  info[1][1].append("[leave, disconnect, dc] - Makes the bot leave the voice channel it's in.")
  info[1][1].append("[play, add] <video name or url> - Plays a video from YouTube, or adds it to the queue if a video is playing.")
  info[1][1].append("[skip, next] - Skips the current video.")
  info[1][1].append("[current, now, playing, np] - Shows the current video.")
  info[1][1].append("[pause, stop] - Pauses the current video.")
  info[1][1].append("[resume, start] - Resumes the current video.")
  info[1][1].append("queue - Shows the queue of videos.")
  info[1][1].append("shuffle - Shuffles the queue.")
  info[1][1].append("clear - Clears the queue.")
  info[1][1].append("[remove, rm, delete, del] <position> - Removes the video at <position> from the queue.")
  info[1][1].append("[move, mv] <position 1> <position 2> - Moves the video at <position 1> to <position 2> in the queue.")
  info[1][1].append("swap <position 1> <position 2> - Swaps the video at <position 1> with the video at <position 2> in the queue.")
  
  info[2][1].append("points - Shows the top 10 NBA leaders in points.")
  info[2][1].append("assists - Shows the top 10 NBA leaders in assists.")
  info[2][1].append("rebounds - Shows the top 10 NBA leaders in rebounds.")
  info[2][1].append("blocks - Shows the top 10 NBA leaders in blocks.")
  info[2][1].append("steals - Shows the top 10 NBA leaders in steals.")
  info[2][1].append("[turnovers, tovs] - Shows the top 10 NBA leaders in turnovers.")
  info[2][1].append("[threes, 3s] - Shows the top 10 NBA leaders in threes.")
  info[2][1].append("[orebounds, orebs] - Shows the top 10 NBA leaders in offensive rebounds.")
  info[2][1].append("[drebounds, drebs] - Shows the top 10 NBA leaders in defensive rebounds.")
  info[2][1].append("[freethrows, fts] - Shows the top 10 NBA leaders in free throws.")
  info[2][1].append("[west, western, westernconference, westconference] - Shows the Western Conference standings.")
  info[2][1].append("[east, eastern, easternconference, eastconference] - Shows the Eastern Conference standings.")
  info[2][1].append("games - Shows the NBA games that are being played today. (Note the games change at 12:00 pm EST)")
  info[2][1].append("arena <team name> - Shows the name of the arena of the specified NBA team.")
  info[2][1].append("[coach, headcoach] <team name> - Shows the name of the Head Coach of the specified NBA team.")
  info[2][1].append("[gm, generalmanager] <team name> - Shows the name of the General Manager of the specified NBA team.")
  info[2][1].append("owner <team name> - Shows the name of the owner of the specified NBA team.")
  info[2][1].append("[stats, s] <player name> - Shows the stats of the specified player in the current season.")
  info[2][1].append("[statspost, sp] <player name> - Shows the stats of the specified player in the current postseason.")
  info[2][1].append("[cstats, careerstats, cs] <player name> - Shows the career stats of the specified player.")
  info[2][1].append("[cstatspost, careerstatspost, csp] <player name> - Shows the career playoff stats of the specified player.")
  info[2][1].append("[sstats, seasonstats, ss] <player name> <season> - Shows the stats of the specified player in the specified season.")
  info[2][1].append("[sstatspost, seasonstatspost, ssp] <player name> <season> - Shows the playoff stats of the specified player in the specified season.")
  info[2][1].append("seasons <player name> - Shows the seasons that the specified player played in.")
  info[2][1].append("[seasonspost, postseasons] <player name> - Shows the playoffs that the specified player played in.")
  info[2][1].append("[homerecord, home] <team name> - Shows the home record of the specified team.")
  info[2][1].append("[awayrecord, away, road, roadrecord] <team name> - Shows the away record of the specifed team.")

  str1 = ""
  for pair in info:
    str1 += "**__" + pair[0] + "__**\n"
    for i in range(len(pair[1])):
      if i == 0:
        str1 += "***"
      str1 += "```" + pair[1][i] + "```"
      if i == len(pair[1]) - 1:
        str1 += "***\n"
      str1 += "\n"

  db["info"] = str1

#-----Show that bot is logged in
@client.event
async def on_ready():
  print("Logged in as {0.user}".format(client) + ".")

@client.event
async def on_guild_join(guild):
  db["guild_symbols"][str(guild.id)] = "$"

@client.event
async def on_guild_remove(guild):
  del db["guild_symbols"][str(guild.id)]

@client.command(aliases=["changesymbol", "changecommand"])
async def changeprefix(ctx, prefix):
  if ctx.message.author.guild_permissions.administrator == True:
    if prefix in db["symbol_list"]:
      db["guild_symbols"][str(ctx.guild.id)] = prefix
      await ctx.send("**Prefix changed to " + prefix + "**")
    else:
      await ctx.send("**Valid prefixes are: " + db["symbols"] + "**")
  else:
    await ctx.send("**Only admins can change the prefix.**")

@client.command(aliases=["information", "commands"])
async def info(ctx):
  embed = discord.Embed(title="**Commands**", description=db["info"], color=0xCCAC00)
  await ctx.send(embed=embed)

#-----Check chat
@client.event
async def on_message(message):
  if message.author == client.user:
    return

  await client.process_commands(message)

asyncio.run(main())