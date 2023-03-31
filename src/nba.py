import discord
import json
import calendar
import nba_api
from discord.ext import commands
from decimal import Decimal, ROUND_HALF_UP
from nba_api.live.nba.endpoints import scoreboard
from nba_api.stats.static import players
from nba_api.stats.static import teams
from nba_api.stats.endpoints import alltimeleadersgrids
from nba_api.stats.endpoints import leaguestandings
from nba_api.stats.endpoints import playerprofilev2
from nba_api.stats.endpoints import teamdetails
from nba_api.stats.library.parameters import SeasonYear

class NBA(commands.Cog):
  def __init__(self, client):
    self.client = client
    self.logos = self.get_logos()

  #-----Functions
  def get_logos(self):
    with open("resources/logos.json", "r") as logos_file:
      logos = json.load(logos_file)
      return logos

  def get_name_loop(self, name):
    new_name = ""
    for i in range(len(name)):
      new_name += name[i]
      if i + 1 < len(name):
        new_name += " "
    return new_name
    
  def get_player(self, name):
    player = []
    
    if len(players.find_players_by_first_name(name)) == 1:
      player = players.find_players_by_first_name(name)[0]
    elif len(players.find_players_by_last_name(name)) == 1:
      player = players.find_players_by_last_name(name)[0]
    else:
      this_player = players.find_players_by_full_name(name)
      if len(this_player) == 1 or len(this_player) == 2:
        player = this_player[0]
  
    return player
  
  def get_team(self, name):
    team = []
  
    if len(teams.find_teams_by_full_name(name)) == 1:
      team = teams.find_teams_by_full_name(name)[0]
    elif len(teams.find_teams_by_nickname(name)) == 1:
      team = teams.find_teams_by_nickname(name)[0]
    elif teams.find_team_by_abbreviation(name):
      team = teams.find_team_by_abbreviation(name)
  
    return team
  
  def name_ends_with_s(self, name):
    if name.endswith("s"):
      name = name + "'"
    else:
      name = name + "'s"
  
    return name
  
  def team_info(self, id, team_name, tricode, info):
    def check_none_team(info):
      if info != None and info != "":
        str1 = "**" + info + "**"
      else:
        str1 = "**" + "N/A" + "**"
      
      return str1
    
    if info == "Home" or info == "Away":
      stands = leaguestandings.LeagueStandings().get_dict()["resultSets"][0]["rowSet"]

      for stand in stands:
        if id in stand:
          if info == "Home":
            record = stand[17].strip().split("-", 1)
          elif info == "Away":
            record = stand[18].strip().split("-", 1)
          record = record[0] + " - " + record[1]
          break

      embed = discord.Embed(title=check_none_team(record), description="***" + self.logos[tricode] + " " + self.name_ends_with_s(team_name) + " " + info + " Record***", color=0x76C4AE)
    else:
      team = teamdetails.TeamDetails(team_id=id).get_dict()["resultSets"][0]["rowSet"][0]
      embed = discord.Embed(description= self.logos[tricode] + " ***" + self.name_ends_with_s(team_name) + " " + info + "***", color = 0x87CEEB)
      
      if info == "Arena":
        embed.title = check_none_team(team[5])
      elif info == "Owner":
        embed.title = check_none_team(team[7])
      elif info == "General Manager":
        embed.title = check_none_team(team[8])
      elif info == "Head Coach":
        embed.title = check_none_team(team[9])
    
    return embed

  def create_stats_embed(self, gs, gp, games_played, stats_dict, embed):
    def check_none(stat):
      if stat == "GS" or stat == "FG3_PCT":
        if stats_dict[stat] != None:
          str1 = str(stats_dict[stat])
        else:
          str1 = "N/A"
      else:
        if stats_dict[stat] != None:
          str1 = str(Decimal(stats_dict[stat]/gp).quantize(Decimal("0.0"), rounding=ROUND_HALF_UP))
        else:
          str1 = "N/A"

      str1 += "***\n"
    
      return str1

    def in_games_played(stat, key):
      return str(Decimal(stats_dict[stat]/games_played[key]).quantize(Decimal("0.0"), rounding=ROUND_HALF_UP))
        
    final_str = ""
    final_str += "***GP: " + str(gp) + "***\n"
    if gs > 0:
      final_str += "***GS: " + str(gs) + "***\n"
    else:
      final_str += "***GS: " + check_none("GS")
    if "mins" in games_played:
      final_str += "***MIN: "  + in_games_played("MIN", "mins") + "***\n"
    else:
      final_str += "***MIN: " + check_none("MIN")
    embed.add_field(name="", value=final_str, inline=True)
    
    final_str = ""
    final_str += "***PTS: " + check_none("PTS")
    if "rebounds" in games_played:
      final_str += "***TRB: "  + in_games_played("REB", "rebounds") + "***\n"
    else:
      final_str += "***TRB: " + check_none("REB")
    final_str += "***AST: " + check_none("AST")
    embed.add_field(name="", value=final_str, inline=True)
    
    final_str = ""
    if "oreb_dreb_stl_blk" in games_played:
      final_str += "***STL: " + in_games_played("STL", "oreb_dreb_stl_blk") + "***\n"
    else:
      final_str += "***STL: " + check_none("STL")
    if "tov" in games_played:
      final_str += "***TOV: " + in_games_played("TOV", "tov") + "***\n"
    else:
      final_str += "***TOV: " + check_none("TOV")
    final_str += "***PF: " + check_none("PF")
    embed.add_field(name="", value=final_str, inline=True)
    
    final_str = ""
    if "oreb_dreb_stl_blk" in games_played:
      final_str += "***BLK: " + in_games_played("BLK", "oreb_dreb_stl_blk") + "***\n"
      final_str += "***OREB: " + in_games_played("OREB", "oreb_dreb_stl_blk") + "***\n"
      final_str += "***DREB: " + in_games_played("DREB", "oreb_dreb_stl_blk") + "***\n"
    else:
      final_str += "***BLK: " + check_none("BLK")
      final_str += "***OREB: " + check_none("OREB")
      final_str += "***DREB: " + check_none("DREB")
    embed.add_field(name="", value=final_str, inline=True)
    
    final_str = ""
    final_str += "***FGM: " + check_none("FGM")
    final_str += "***FGA: " + check_none("FGA")
    final_str += "***FG%: " + str(stats_dict["FG_PCT"]) + "***\n"
    embed.add_field(name="", value=final_str, inline=True)
    
    final_str = ""
    if "3p_3pa_3pct" in games_played:
      final_str += "***3PM: " + in_games_played("FG3M", "3p_3pa_3pct") + "***\n"
      final_str += "***3PA: " + in_games_played("FG3A", "3p_3pa_3pct") + "***\n"
    else:
      final_str += "***3PM: " + check_none("FG3M")
      final_str += "***3PA: " + check_none("FG3A")
    final_str += "***3P%: " + check_none("FG3_PCT")
    embed.add_field(name="", value=final_str, inline=True)
    
    final_str = ""
    final_str += "***FTM: " + check_none("FTM")
    final_str += "***FTA: " + check_none("FTA")
    final_str += "***FT%: " + str(stats_dict["FT_PCT"]) + "***\n"
    embed.add_field(name="", value=final_str, inline=True)

    return embed

  def less_than_1981(self, first_season, player_seasons):
    games_played = {}
    gs = 0
    
    if first_season < 1981:
      for i in range(len(player_seasons)):
        season = int(player_seasons[i][1].split("-", 1)[0])
  
        def add_games_played(stat):
          if stat not in games_played:
            games_played[stat] = player_seasons[i][6]
          else:
            games_played[stat] = games_played[stat] + player_seasons[i][6]
              
        if season >= 1979:
          add_games_played("3p_3pa_3pct")
          add_games_played("tov")
          add_games_played("oreb_dreb_stl_blk")
          add_games_played("mins")
          add_games_played("rebounds")
        elif season >= 1977:
          add_games_played("tov")
          add_games_played("oreb_dreb_stl_blk")
          add_games_played("mins")
          add_games_played("rebounds")
        elif season >= 1973:
          add_games_played("oreb_dreb_stl_blk")
          add_games_played("mins")
          add_games_played("rebounds")
        elif season >= 1951:
          add_games_played("mins")
          add_games_played("rebounds")
        elif season >= 1950:
          add_games_played("rebounds")
  
        if player_seasons[i][7] != None:
          gs += player_seasons[i][7]

    return games_played, gs
  
  def calculate_career_stats(self, player, type):
    player_name = player["full_name"]
    player_id = player["id"]
    player_stats = playerprofilev2.PlayerProfileV2(player_id=player_id).get_dict()["resultSets"]

    if type == "seasons" or type == "postseasons":
      def seasons_loop(type):
        seasons_played = 0
        season_checker = []

        def find_season(type):
          for i in range(len(player_stats)):
            if player_stats[i]["name"] == type:
              return player_stats[i]["rowSet"]
        
        if type == "seasons":
          embed = discord.Embed(title="**" + self.name_ends_with_s(player_name) + " Seasons Played:**", description="", color=0x3A5311)
          seasons = find_season("SeasonTotalsRegularSeason")
          end = "Seasons"
        elif type == "postseasons":
          embed = discord.Embed(title="**" + self.name_ends_with_s(player_name) + " Post Seasons Played:**", description="", color=0x028A0F)
          seasons = find_season("SeasonTotalsPostSeason")
          end = "Post Seasons"

        for i in range(len(seasons)):
          if seasons[i][1] not in season_checker:
            seasons_played += 1
            embed.description += "***__" + seasons[i][1] + "__ | "
            if seasons[i][4] in self.logos:
              team = self.logos[seasons[i][4]] + " " + seasons[i][4]
            else:
              team = seasons[i][4]
            if i != len(seasons) - 1:
              j = i + 1
              while j < len(seasons) and seasons[j][1] == seasons[i][1]:
                if seasons[j][4] != "TOT":
                  if seasons[j][4] in self.logos:
                    team += ", " + self.logos[seasons[j][4]] + " " + seasons[j][4]
                  else:
                    team += ", " + seasons[j][4]
                j += 1
            embed.description += team + " | Age: " + str(seasons[i][5]).split(".", 1)[0] + "***\n\n"
            season_checker.append(seasons[i][1])
            
        embed.description += "\n***Total " + end + " Played: " + str(seasons_played) + "***"
        return embed
          
      embed = seasons_loop(type)
    else:
      headers = []
      stats = []
      
      def stats_loop(season_totals, type):
        seasons = []
        for s in player_stats:
          if s["name"] == season_totals:
            seasons = s["rowSet"]
          if s["name"] == type:
            if type.startswith("Season"):
              stats = s["rowSet"][-1]
            else:
              stats = s["rowSet"][0]
            headers = s["headers"]
            break
        return seasons, stats, headers
    
      if type == "regular":
        player_seasons, stats, headers = stats_loop("SeasonTotalsRegularSeason", "CareerTotalsRegularSeason")
        first_season = int(player_seasons[0][1].split("-", 1)[0])
        embed_header = "Career Stats:"
        embed_color = 0xC0C0C0
      elif type == "post":
        player_seasons, stats, headers = stats_loop("SeasonTotalsPostSeason", "CareerTotalsPostSeason")
        first_season = int(player_seasons[0][1].split("-", 1)[0])
        embed_header = "Career Playoff Stats:"
        embed_color = 0xFFD700
      else:
        year = str(SeasonYear.default) + "-" + str(SeasonYear.default + 1)[-2:]
  
        if player["is_active"] == True:
          if type == "seasonRegular":
            player_seasons, stats, headers = stats_loop("SeasonTotalsRegularSeason", "SeasonTotalsRegularSeason")
            embed_header = year + " Season Stats:"
            embed_color = 0xB76E79
          elif type == "seasonPost":
            player_seasons, stats, headers = stats_loop("SeasonTotalsPostSeason", "SeasonTotalsPostSeason")
            embed_header = year + " Playoff Stats:"
            embed_color = 0x528AAE
  
            if stats[1] != year:
              return "**Either the " + year + " playoffs have not yet started, or " +  player_name + " has not played in playoffs.**"
          first_season = int(player_seasons[0][1].split("-", 1)[0])
        else:
          if type == "seasonRegular":
            err = " season."
          else:
            err = " playoffs."
          return "**" + player_name + " has not played in the " + year + err + "**"
        
      stats_dict = {}
      games_played, gs = self.less_than_1981(first_season, player_seasons)
               
      for i in range(len(stats)):
        stats_dict[headers[i]] = stats[i]
    
      embed = discord.Embed(title="**" + self.name_ends_with_s(player_name) + " " + embed_header + "**", description="", color=embed_color)
      embed = self.create_stats_embed(gs, stats_dict["GP"], games_played, stats_dict, embed)
    
    return embed

  def get_specific_stats(self, player, type, season):
    player_name = player["full_name"]
    player_id = player["id"]
    player_stats = playerprofilev2.PlayerProfileV2(player_id=player_id).get_dict()["resultSets"]

    def get_seasons(type):
      if type == "regular":
        name = "SeasonTotalsRegularSeason"
      elif type == "post":
        name = "SeasonTotalsPostSeason"

      for i in range(len(player_stats)):
        if player_stats[i]["name"] == name:
          return player_stats[i]["headers"], player_stats[i]["rowSet"]

    if type == "regular":
      headers, seasons = get_seasons("regular")
      embed_header = season + " Season Stats:**"
      embed_color = 0x6497B1
      err = "season."
    elif type == "post":
      headers, seasons = get_seasons("post")
      embed_header = season + " Playoff Stats:**"
      embed_color = 0xFF77AA
      err = "playoffs."

    stats = []

    for i in range(len(seasons)):
      if i == 0:
        first_season = int(seasons[i][1].split("-", 1)[0])
      if season in seasons[i]:
        stats = seasons[i]
        break

    if stats != []:
      stats_dict = {}
      games_played, gs = self.less_than_1981(first_season, [stats])

      for i in range(len(stats)):
        stats_dict[headers[i]] = stats[i]

      embed = discord.Embed(title="**" + self.name_ends_with_s(player_name) + " " + embed_header, description="", color=embed_color)
      embed = self.create_stats_embed(gs, stats_dict["GP"], games_played, stats_dict, embed)
      return embed

    return "**" + player_name + " did not play in the " + season + " " + err + "**"

  def nba_leaders(self, data_header, print_header):
    leaders = alltimeleadersgrids.AllTimeLeadersGrids()
    leaders_set = leaders.get_dict()["resultSets"]
    temp = ""
    
    for s in leaders_set:
      if s['name'] == data_header:
        leaders_list = s["rowSet"]
        for l in leaders_list:
          temp +=  "***" + str(l[3]) + ") " + l[1] + " - " + str(l[2]) + "***\n"
        embed = discord.Embed(title="**" + print_header + "**", description=temp, color=0x008080)
        return embed
        
  def nba_standings(self, data_conference, header_conference):
    stands = leaguestandings.LeagueStandings().get_dict()["resultSets"][0]["rowSet"]
    position = 1
    result_str = ""
    
    for stand in stands:
      if stand[5] == data_conference:
        team_tricode = teams.find_team_name_by_id(stand[2])["abbreviation"]
        team_name = stand[4]
        result_str +=  "***" + str(position) + ") " + self.logos[team_tricode] + " " + team_name + " (" + stand[16] + ")***\n"
        position += 1
        
    embed = discord.Embed(title="**" + header_conference + " Conference Standings:**", description=result_str, color=0x7851a9)
    return embed
  
  def nba_games(self, header, games):
    current_games = ""
    scheduled_games = ""
    finished_games = ""
  
    for i in range(len(games)):
      status = games[i]["gameStatusText"]
      away_team = games[i]["awayTeam"]["teamTricode"]
      home_team = games[i]["homeTeam"]["teamTricode"]
      away_team_score = games[i]["awayTeam"]["score"]
      home_team_score = games[i]["homeTeam"]["score"]
  
      if "ET" in status:
        scheduled_games += "***" + self.logos[away_team] + " " + away_team + "  at  " + home_team +  " " + self.logos[home_team] + " | " + status + "***\n\n"
      elif "Final" in status:
        if away_team_score > home_team_score:
           finished_games += self.logos[away_team] + " __***" + away_team + " " + str(away_team_score) + "***__*** - " + str(home_team_score) + " " + home_team + " " + self.logos[home_team] + "***\n\n"
        else:
          finished_games += self.logos[away_team] + " ***" + away_team + " " + str(away_team_score) + " - ***__***" + str(home_team_score) + " " + home_team + "***__ " + self.logos[home_team] + "\n\n"
      else:    
        current_games +=  "***" + self.logos[away_team] + " " + away_team + " " + str(away_team_score) + " - " + str(home_team_score) + " " + home_team + " " + self.logos[home_team] + " "
        
        if "Half" in status:
          current_games += " | " + "Halftime***\n\n"
        elif "Tipoff" in status:
          current_games += " | " + "Tipoff***\n\n"
        elif "Qtr" in status:
          status = status.split(" ", 1)
          current_games += " | " + status[1] + ": " + status[0] + "***\n\n"
        else:
          status = status.split(" ", 1)
          current_games += " | " + status[0] + ": " + status[1] + "***\n\n"
    
    embed = discord.Embed(title="**NBA Games on " + header + ":**", color=0xFF5733)
    # embed.description = current_games + scheduled_games
    if current_games != "":
      embed.add_field(name="**Live Games:**", value=current_games, inline=False)
      if scheduled_games != "" or finished_games != "":
        embed.add_field(name="", value="", inline=False)
  
    if scheduled_games != "":
      embed.add_field(name="**Scheduled Games:**", value=scheduled_games, inline=False)
      if finished_games != "":
        embed.add_field(name="", value="", inline=False)
  
    if finished_games != "":
      embed.add_field(name="**Finished Games:**", value=finished_games, inline=False)

    return embed
  
  @commands.command()
  async def points(self, ctx):
    embed = self.nba_leaders("PTSLeaders", "Point Leaders")
    await ctx.send(embed=embed)

  @commands.command()
  async def rebounds(self, ctx):
    embed = self.nba_leaders("REBLeaders", "Rebound Leaders")
    await ctx.send(embed=embed)

  @commands.command()
  async def assists(self, ctx):
    embed = self.nba_leaders("ASTLeaders", "Assist Leaders")
    await ctx.send(embed=embed)

  @commands.command()
  async def blocks(self, ctx):
    embed = self.nba_leaders("BLKLeaders", "Block Leaders")
    await ctx.send(embed=embed)

  @commands.command()
  async def steals(self, ctx):
    embed = self.nba_leaders("STLLeaders", "Steal Leaders")
    await ctx.send(embed=embed)

  @commands.command(aliases=["tovs"])
  async def turnovers(self, ctx):
    embed = self.nba_leaders("TOVLeaders", "Turnover Leaders")
    await ctx.send(embed=embed)

  @commands.command(aliases=["3s"])
  async def threes(self, ctx):
    embed = self.nba_leaders("FG3MLeaders", "Three Leaders")
    await ctx.send(embed=embed)

  @commands.command(aliases=["orebs"])
  async def orebounds(self, ctx):
    embed = self.nba_leaders("OREBLeaders", "Offensive Rebound Leaders")
    await ctx.send(embed=embed)

  @commands.command(aliases=["drebs"])
  async def drebounds(self, ctx):
    embed = self.nba_leaders("DREBLeaders", "Defensive Rebound Leaders")
    await ctx.send(embed=embed)

  @commands.command(aliases=["fts"])
  async def freethrows(self, ctx):
    embed = self.nba_leaders("FTMLeaders", "Free Throw Leaders")
    await ctx.send(embed=embed)

  async def standings_helper(self, ctx, data_header, output_header):
    try:
      embed = self.nba_standings(data_header, output_header)
      await ctx.send(embed=embed)
    except:
      await ctx.send("**No standings to display at the moment.**")

  @commands.command(aliases=["western", "westernconference", "westconference"])
  async def west(self, ctx):
    await self.standings_helper(ctx, "West", "Western")

  @commands.command(aliases=["eastern", "easternconference", "eastconference"])
  async def east(self, ctx):
    await self.standings_helper(ctx, "East", "Eastern")

  async def team_info_helper(self, ctx, name, mode):
    if len(name) >= 1 and len(name) <= 5:
      input_name = self.get_name_loop(name)
      team = self.get_team(input_name)

      if team != []:
          embed = self.team_info(team["id"], team["full_name"], team["abbreviation"], mode)
          await ctx.send(embed=embed)
      else:
        await ctx.send("**Team not found.**")
    else:
      await ctx.send("**Invalid input.**")

  @commands.command()
  async def arena(self, ctx, *name):
    await self.team_info_helper(ctx, name, "Arena")

  @commands.command(aliases=["headcoach"])
  async def coach(self, ctx, *name):
    await self.team_info_helper(ctx, name, "Head Coach")

  @commands.command(aliases=["generalmanager"])
  async def gm(self, ctx, *name):
    await self.team_info_helper(ctx, name, "General Manager")

  @commands.command()
  async def owner(self, ctx, *name):
    await self.team_info_helper(ctx, name, "Owner")

  async def stats_helper(self, ctx, name, mode):
    if len(name) >= 1 and len(name) <= 5:
      input_name = self.get_name_loop(name)
      player = self.get_player(input_name)

      if player != []:
          embed = self.calculate_career_stats(player, mode)
          if isinstance(embed, str):
            await ctx.send(embed)
          else:
            await ctx.send(embed=embed)
      else:
        await ctx.send("**Player not found.**")
    else:
      await ctx.send("**Input only allows for first name, last name, or first name and last name.**")

  @commands.command(aliases=["careerstats", "cs"])
  async def cstats(self, ctx, *name):
    await self.stats_helper(ctx, name, "regular")

  @commands.command(aliases=["careerstatspost", "csp"])
  async def cstatspost(self, ctx, *name):
    await self.stats_helper(ctx, name, "post")

  @commands.command(aliases=["s"])
  async def stats(self, ctx, *name):
    await self.stats_helper(ctx, name, "seasonRegular")

  @commands.command(aliases=["sp"])
  async def statspost(self, ctx, *name):
    await self.stats_helper(ctx, name, "seasonPost")

  @commands.command()
  async def seasons(self, ctx, *name):
    await self.stats_helper(ctx, name, "seasons")

  @commands.command(aliases=["seasonspost"])
  async def postseasons(self, ctx, *name):
    await self.stats_helper(ctx, name, "postseasons")

  @commands.command(aliases=["home"])
  async def homerecord(self, ctx, *name):
    await self.team_info_helper(ctx, name, "Home")

  @commands.command(aliases=["away", "road", "roadrecord"])
  async def awayrecord(self, ctx, *name):
    await self.team_info_helper(ctx, name, "Away")

  @commands.command(aliases=["seasonstats", "ss"])
  async def sstats(self, ctx, *info):
    await self.sstats_helper(ctx, info, "regular")

  @commands.command(aliases=["seasonstatspost", "ssp"])
  async def sstatspost(self, ctx, *info):
    await self.sstats_helper(ctx, info, "post")

  async def sstats_helper(self, ctx, info, mode):
    
    async def helper(ctx, season):
      player = self.get_name_loop(info[0:len(info) - 1])
      player = self.get_player(player)

      if player != []:
        embed = self.get_specific_stats(player, mode, season)
        if isinstance(embed, str):
          await ctx.send(embed)
        else:
          await ctx.send(embed=embed)
      else:
        await ctx.send("**Player not found.**")
      
    if len(info) >= 2 and len(info) <= 6:
      season = info[len(info) - 1]
      if "-" in season:
        season_check = season.split("-", 1)
        if season_check[0].isdigit() and season_check[1].isdigit():
          await helper(ctx, season)
        else:
          await ctx.send("**Did not enter a season.**")
      else:
        if season.isdigit():
          season = str(season) + "-" + str(int(season)+1)[-2:]
          await helper(ctx, season)
        else:
          await ctx.send("**Did not enter a season.**")
    else:
      await ctx.send("**Invalid input.**")

  @commands.command()
  async def games(self, ctx):
    try:
      this_scoreboard = scoreboard.ScoreBoard()
      game_date = this_scoreboard.get_dict()["scoreboard"]["gameDate"]
      games = this_scoreboard.games.get_dict()
  
      if games:
        game_date = game_date.split("-")
        if game_date[1][0] == "0":
          game_date[1] == game_date[1][1]
        game_date[1] = calendar.month_name[int(game_date[1])]
        game_date = game_date[1] + " " + game_date[2] + ", " + game_date[0]
        embed = self.nba_games(game_date, games)
        await ctx.send(embed=embed)
      else:
        await ctx.send("**No games to display at the moment.**")
    except:
      await ctx.send("**No games to display at the moment.**")
    
async def setup(client):
  await client.add_cog(NBA(client))