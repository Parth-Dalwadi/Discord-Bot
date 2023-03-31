import discord
import random
import nacl
from discord.ext import commands
import yt_dlp as youtube_dl

class Music(commands.Cog):
  def __init__(self, client):
    self.client = client
    self.queue = {}
    self.is_playing = {}
    self.FFMPEG_OPTIONS = {
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", 
        "options": "-vn"
    }
    self.YDL_OPTIONS = {
      "format": "bestaudio", 
      "quiet": True
    }
    self.title = {}
    self.channel = {}
    self.duration = {}
    self.thumbnail = {}

  @commands.Cog.listener()
  async def on_voice_state_update(self, member, before, after):
    client = "{0.user}".format(self.client)
    if str(member) == client:
      if after.channel is None:
        if member.guild.id in self.is_playing:
          del self.is_playing[member.guild.id]

        if member.guild.id in self.queue:
          del self.queue[member.guild.id]

        if member.guild.id in self.title:
          del self.title[member.guild.id]

        if member.guild.id in self.channel:
          del self.channel[member.guild.id]

        if member.guild.id in self.duration:
          del self.duration[member.guild.id]

        if member.guild.id in self.thumbnail:
          del self.thumbnail[member.guild.id]

  @commands.command()
  async def join(self, ctx):
    if ctx.author.voice is None:
      await ctx.send("**You're not in a voice channel.**")
    else:
      voice_channel = ctx.author.voice.channel
      if ctx.voice_client is None or ctx.voice_client.channel != voice_channel:
        self.is_playing[ctx.guild.id] = False
        if ctx.voice_client is None:
          self.queue[ctx.guild.id] = []
          await voice_channel.connect()
        else:
          self.queue[ctx.guild.id].clear()
          await ctx.voice_client.move_to(voice_channel)
      else:
        await ctx.send("**Already in the voice channel.**")

  @commands.command(aliases=["disconnect", "dc"])
  async def leave(self, ctx):
    is_admin = ctx.message.author.guild_permissions.administrator
    
    if ctx.voice_client is not None:
      if is_admin == True or ctx.author.voice is not None:
        if is_admin == True or ctx.voice_client.channel == ctx.author.voice.channel:
          await ctx.voice_client.disconnect()
        else:
          await ctx.send("**Can't disconnect the bot unless you're in the same channel.**")
      else:
        await ctx.send("**Can't disconnect the bot unless you're in the same channel.**")
    else:
      await ctx.send("**Already not in voice channel.**")

  @commands.command(aliases=["add"])
  async def play(self, ctx, *url):
    is_admin = ctx.message.author.guild_permissions.administrator
    
    if ctx.voice_client is not None:
      if is_admin == True or ctx.author.voice is not None:
        if is_admin == True or ctx.voice_client.channel == ctx.author.voice.channel:
          try:
            vc = ctx.voice_client
            with youtube_dl.YoutubeDL(self.YDL_OPTIONS) as ydl:
              if len(url) == 1:
                info = ydl.extract_info(url[0], download=False)
              else:
                info = ydl.extract_info(f"ytsearch:{url}", download=False)['entries'][0]
              
              url2 = info["url"]
              title_url = str(info.get('webpage_url', None))
              temp_title = str(info.get('title', None))
              title = f"[{temp_title}]({title_url})"
              channel = str(info.get('channel', None))
              duration = info.get('duration', None)
              thumbnail = str(info.get('thumbnail', None))
              mins = str(duration//60)
              seconds = str(duration%60)
        
              if len(seconds) < 2:
                seconds = "0" + seconds
        
              duration = mins + ":" + seconds
              
            if self.is_playing[ctx.guild.id] == True:
              self.queue[ctx.guild.id].append([url2, title, channel, duration, thumbnail])
              embed = discord.Embed(title="**Song added:**", description="***" + title + "***", color=0x4B0082)
              embed.add_field(name="**Channel:**", value="***" + channel + "***", inline=True)
              embed.add_field(name="**Duration:**", value="***" + duration + "***", inline=True)
              embed.add_field(name="**Queue Position:**", value="***" + str(len(self.queue[ctx.guild.id])) + "***", inline=True)
              embed.set_thumbnail(url=thumbnail)
              await ctx.send(embed=embed)
            else:
              self.is_playing[ctx.guild.id] = True
              self.title[ctx.guild.id] = title
              self.channel[ctx.guild.id] = channel
              self.duration[ctx.guild.id] = duration
              self.thumbnail[ctx.guild.id] = thumbnail
              source = await discord.FFmpegOpusAudio.from_probe(url2, **self.FFMPEG_OPTIONS)
              vc.play(source, after=lambda e: self.play_next(ctx))
              await ctx.invoke(self.client.get_command("current"))
          except:
            await ctx.send("**Either link is not valid, or video was not located.**")
        else:
          await ctx.send("**Can't play a video if you're not in the same channel.**")
      else:
        await ctx.send("**Can't play a video if you're not in the same channel.**")
    else:
      await ctx.send("**Not in a channel - can't play a video.**")

  def play_next(self, ctx):
    if len(self.queue[ctx.guild.id]) > 0:
      vc = ctx.voice_client
      queue = self.queue[ctx.guild.id]
      url = queue[0][0]
      self.title[ctx.guild.id] = queue[0][1]
      self.channel[ctx.guild.id] = queue[0][2]
      self.duration[ctx.guild.id] = queue[0][3]
      self.thumbnail[ctx.guild.id] = queue[0][4]
      self.queue[ctx.guild.id].pop(0)
      vc.play(discord.FFmpegOpusAudio(url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next(ctx))
    else:
      self.is_playing[ctx.guild.id] = False

  @commands.command(aliases=["next"])
  async def skip(self, ctx):
    is_admin = ctx.message.author.guild_permissions.administrator

    if ctx.guild.id in self.is_playing:
      if self.is_playing[ctx.guild.id] == True:
        if is_admin == True or ctx.author.voice is not None:
          if is_admin == True or ctx.voice_client.channel == ctx.author.voice.channel:
            ctx.voice_client.stop()
            await ctx.send("**Song has been skipped.**")
          else:
            await ctx.send("**Can't skip a song if you're not in the same voice channel.")
        else:
          await ctx.send("**Can't skip a song if you're not in the same voice channel.")
      else:
        await ctx.send("**No songs in queue.**")
    else:
      await ctx.send("**Not in a voice chat - nothing to skip.**")

  @commands.command(aliases=["now", "np", "playing"])
  async def current(self, ctx):
    if ctx.guild.id in self.is_playing:
      if self.is_playing[ctx.guild.id] == True:
        embed = discord.Embed(title="**Current Song:**", description= "***" + self.title[ctx.guild.id] + "***", color=0x8B0000)
        embed.add_field(name="**Channel:**", value= "***" + self.channel[ctx.guild.id] + "***", inline=True)
        embed.add_field(name="**Duration:**", value= "***" + self.duration[ctx.guild.id] + "***", inline=True)
        embed.set_thumbnail(url=self.thumbnail[ctx.guild.id])
        await ctx.send(embed=embed)
      else:
        await ctx.send("**No song is being played currently.**")
    else:
      await ctx.send("**Not in a voice chat - nothing is being played currently.**")
  
  @commands.command(aliases=["stop"])
  async def pause(self, ctx):
    is_admin = ctx.message.author.guild_permissions.administrator
    
    if ctx.guild.id in self.is_playing:
      if self.is_playing[ctx.guild.id] == True:
        if is_admin == True or ctx.author.voice is not None:
          if is_admin == True or ctx.voice_client.channel == ctx.author.voice.channel: 
            await ctx.send("**CP3 has stopped playing.**")
            await ctx.voice_client.pause()
          else:
            await ctx.send("**Can't pause the song if you're not in the same voice channel.**")
        else:
          await ctx.send("**Can't pause the song if you're not in the same voice channel.**")
      else:
        await ctx.send("**No song to pause.**")
    else:
      await ctx.send("**Not in a voice chat - no song to pause.**")

  @commands.command(aliases=["start"])
  async def resume(self, ctx):
    is_admin = ctx.message.author.guild_permissions.administrator
    
    if ctx.guild.id in self.is_playing:
      if self.is_playing[ctx.guild.id] == True:
        if is_admin == True or ctx.author.voice is not None:
          if is_admin == True or ctx.voice_client.channel == ctx.author.voice.channel:
            await ctx.send("**CP3 has resumed.**")
            await ctx.voice_client.resume()
          else:
            await ctx.send("**Can't resume the song if you're not in the same voice channel.**")
        else:
          await ctx.send("**Can't resume the song if you're not in the same voice channel.**")
      else:
        await ctx.send("**No song to resume.**")
    else:
      await ctx.send("**Not in a voice chat - no song to resume.**")

  @commands.command()
  async def queue(self, ctx):
    if ctx.guild.id in self.is_playing:
      if self.queue[ctx.guild.id] != []:
        embed_template = discord.Embed(title="**Queue:**", description="", color=0x670A0A)
        embeds = [embed_template]
        embed_index = 0
        for i in range(len(self.queue[ctx.guild.id])):
          str1 = "***" + str(i+1) + ") " + str(self.queue[ctx.guild.id][i][1]) + "***\n"

          if len(embeds[embed_index].description) + len (str1) > 4096:
            embeds.append(discord.Embed(title="**Queue Continued:**", description=str1, color=0x670A0A))
            embed_index += 1

          embeds[embed_index].description += str1
  
        for embed in embeds:
          await ctx.send(embed=embed)
      else:
        await ctx.send("**No songs in queue.**")
    else:
      await ctx.send("**Not in a voice chat - no songs in queue.**")

  @commands.command()
  async def shuffle(self, ctx):
    is_admin = ctx.message.author.guild_permissions.administrator
    
    if ctx.guild.id in self.is_playing:
      if self.queue[ctx.guild.id] != []:
        if is_admin == True or ctx.author.voice is not None:
          if is_admin == True or ctx.voice_client.channel == ctx.author.voice.channel:
            if len(self.queue[ctx.guild.id]) > 1:
              random.shuffle(self.queue[ctx.guild.id])
              await ctx.invoke(self.client.get_command("queue"))
            else:
              await ctx.send("**Need more than one song in queue to shuffle.**")
          else:
            await ctx.send("**Can't shuffle the queue if you're not in the same voice channel.**")
        else:
          await ctx.send("**Can't shuffle the queue if you're not in the same voice channel.**")
      else:
        await ctx.send("**Queue is empty.**")
    else:
      await ctx.send("**Not in a voice chat - queue is empty.**")

  @commands.command()
  async def clear(self, ctx):
    is_admin = ctx.message.author.guild_permissions.administrator
    
    if ctx.guild.id in self.is_playing:
      if self.queue[ctx.guild.id] != []:
        if is_admin == True or ctx.author.voice is not None:
          if is_admin == True or ctx.voice_client.channel == ctx.author.voice.channel:
            self.queue[ctx.guild.id].clear()
            await ctx.send("**Queue has been cleared.**")
          else:
            await ctx.send("**Can't clear the queue if you're not in the same voice channel.**")
        else:
          await ctx.send("**Can't clear the queue if you're not in the same voice channel.**")
      else:
        await ctx.send("**Queue is already empty.**")
    else:
      await ctx.send("**Not in a voice chat - queue is already empty.**")

  @commands.command(aliases=["rm", "delete", "del"])
  async def remove(self, ctx, pos):
    is_admin = ctx.message.author.guild_permissions.administrator
    
    if ctx.guild.id in self.is_playing:
      if self.queue[ctx.guild.id] != []:
        if is_admin == True or ctx.author.voice is not None:
          if is_admin == True or ctx.voice_client.channel == ctx.author.voice.channel:
            if pos.isnumeric():
              pos = int(pos)
              if pos > 0 and pos <= len(self.queue[ctx.guild.id]):
                pos -= 1
                title = self.queue[ctx.guild.id][pos][1]
                thumbnail = self.queue[ctx.guild.id][pos][4]
                embed = discord.Embed(title="**Song Removed:**", description="***" + title + "***", color=0x355E3B)
                embed.set_thumbnail(url=thumbnail)
                self.queue[ctx.guild.id].pop(pos)
                await ctx.send(embed=embed)
              else:
                await ctx.send("**Position " + str(pos) + " is invalid.**")
            else:
              await ctx.send("**Invalid input.**")
          else:
            await ctx.send("**Can't remove a song from the queue if you're not in the same voice channel.**")
        else:
          await ctx.send("**Can't remove a song from the queue if you're not in the same voice channel.**")
      else:
        await ctx.send("**Queue is empty.**")
    else:
      await ctx.send("**Not in a voice chat - queue is empty.**")
      
  @commands.command(aliases=["mv"])
  async def move(self, ctx, pos1, pos2):      
    await self.move_swap_helper(ctx, pos1, pos2, "move")

  @commands.command()
  async def swap(self, ctx, pos1, pos2):
    await self.move_swap_helper(ctx, pos1, pos2, "swap")

  async def move_swap_helper(self, ctx, pos1, pos2, mode):
    is_admin = ctx.message.author.guild_permissions.administrator
    
    if ctx.guild.id in self.is_playing:
      if self.queue[ctx.guild.id] != []:
        if is_admin == True or ctx.author.voice is not None:
          if is_admin == True or ctx.voice_client.channel == ctx.author.voice.channel:
            if pos1.isnumeric() and pos2.isnumeric():
              pos1 = int(pos1)
              pos2 = int(pos2)
              if pos1 > 0 and pos1 <= len(self.queue[ctx.guild.id]) and pos2 > 0 and pos2 <= len(self.queue[ctx.guild.id]) and pos1 != pos2:
                pos1 -= 1
                pos2 -= 1
      
                if mode == "move":
                  if pos1 < pos2:
                    self.queue[ctx.guild.id].insert(pos2 + 1, self.queue[ctx.guild.id][pos1])
                    self.queue[ctx.guild.id].pop(pos1)
                  else:
                    self.queue[ctx.guild.id].insert(pos2, self.queue[ctx.guild.id][pos1])
                    self.queue[ctx.guild.id].pop(pos1 + 1)
                elif mode == "swap":
                  temp = self.queue[ctx.guild.id][pos1]
                  self.queue[ctx.guild.id][pos1] = self.queue[ctx.guild.id][pos2]
                  self.queue[ctx.guild.id][pos2] = temp
      
                await ctx.invoke(self.client.get_command("queue"))
              else:
                await ctx.send("**Positions are not valid.**")
            else:
              await ctx.send("**Invalid inputs.**")
          else:
            await ctx.send("**Can't move or swap a video if you're not in the same voice channel.**")
        else:
          await ctx.send("**Can't move or swap a video if you're not in the same voice channel.**")
      else:
        await ctx.send("**Queue is empty.**")
    else:
      await ctx.send("**Not in a voice chat - queue is empty.**")

async def setup(client):
  await client.add_cog(Music(client))