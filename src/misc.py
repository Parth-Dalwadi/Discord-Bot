import discord
import random
import json
from discord.ext import commands

class Misc(commands.Cog):
  def __init__(self, client):
    self.client = client
    self.cp3 = self.load_json("cp3.json")
    self.highlights = self.load_json("highlights.json")

  def load_json(self, name):
    with open("resources/" + name, "r") as file:
      json_dict = json.load(file)
      return json_dict

  def random_video(self, name):
    if name == "cp3":
      return random.choice(self.cp3["videos"])
    elif name == "highlights":
      return random.choice(self.highlights["videos"])

  def all_videos(self, name):
    embed_template = discord.Embed(title="**" + name + "**", description="", color=0xB87333)
    embeds = [embed_template]
    
    if name == "CP3":
      titles = self.cp3["titles"]
      videos = self.cp3["videos"]
    elif name == "Highlights":
      titles = self.highlights["titles"]
      videos = self.highlights["videos"]

    embed_index = 0

    for i in range(len(titles)):
      str1 = f"***{str(i+1)}: [{titles[i]}]({videos[i]})***\n"

      if len(embeds[embed_index].description) + len(str1) > 4096:
        embeds.append(discord.Embed(title="**" + name + " Continued" + "**", description="", color=0xB87333))
        embed_index += 1

      embeds[embed_index].description += str1

    return embeds

  @commands.command()
  @commands.bot_has_permissions(send_messages=True, embed_links=True)
  async def cp3(self, ctx):
    await ctx.send(self.random_video("cp3"))

  @commands.command(aliases=["hl", "hls"])
  @commands.bot_has_permissions(send_messages=True, embed_links=True)
  async def highlights(self, ctx):
    await ctx.send(self.random_video("highlights"))

  @commands.command()
  @commands.bot_has_permissions(send_messages=True, embed_links=True)
  async def allcp3(self, ctx):
    embeds = self.all_videos("CP3")
    for embed in embeds:
      await ctx.send(embed=embed)

  @commands.command(aliases=["allhl", "allhls"])
  @commands.bot_has_permissions(send_messages=True, embed_links=True)
  async def allhighlights(self, ctx):
    embeds = self.all_videos("Highlights")
    for embed in embeds:
      await ctx.send(embed=embed)

async def setup(client):
  await client.add_cog(Misc(client))