import json
import urllib.request
from enum import Enum
from collections import namedtuple
import datetime

# Python wrapper for the OWL web API.
class OwlApi:
  class EndPoints(Enum):
    SCHEDULE = 0
    NUM_ELEMENTS = 1
    INVALID = -1

  owl_url = "https://api.overwatchleague.com/"
  api_endpoints = {
    EndPoints.SCHEDULE: "schedule",
  }
  
  def Schedule(self):
    response = urllib.request.urlopen(owl_url + api_endpoints[EndPoints.SCHEDULE])
    return json.load(response)    

class OverwatchMap(Enum):
  class MapType(Enum):
    INVALID = -1
    ASSAULT = 0
    CONTROL = 1
    ESCORT = 2
    HYBRID = 3
    
  INVALID = -1
  
  ANUBIS = 0
  HANAMURA = 1
  VOLSKAYA = 2
  
  ILLIOS = 3
  LIJIANG_TOWER = 4
  NEPAL = 5
  
  DORADO = 6
  GIBRALTAR = 7
  ROUTE_66 = 8
  
  HOLLYWOOD = 9
  KINGS_ROW = 10
  NUMBANI = 11
  
  EICHENWALD = 12
  OASIS = 13
  HORIZON = 14
  JUNKERTOWN = 15
  BLIZZARD_WORLD = 16
  
  def GetMapType(map):
    if map == ANUBIS or map == HANAMURA or map == VOLSKAYA or map == HORIZON:
      return MapType.ASSAULT
    elif map == ILLIOS or map == LIJIANG_TOWER or map == NEPAL or map == OASIS:
      return MapType.CONTROL
    elif map == DORADO or map == GIBRALTAR or map == ROUTE_66 or map == JUNKERTOWN:
      return MapType.ESCORT
    elif map == HOLLYWOOD or map == KINGS_ROW or map == NUMBANI or map == EICHENWALD or map == BLIZZARD_WORLD:
      return MapType.HYBRID
    return MapType.INVALID
    
# Represents a team in OWL. Records team name, abbreviation, rating, and record.
class OwlTeam:
  TeamRecord = namedtuple("TeamRecord", ["wins", "losses", "ties"])

  def __init__(self, id, name, abbr, rating = None):
    self.id = id
    self.name = name
    self.abbr = abbr
    self.rating = rating
    self.record = OwlTeam.TeamRecord(0, 0, 0)
    self.map_score = OwlTeam.TeamRecord(0, 0, 0)
    
  def __str__(self):
    return self.__repr__()
    
  def __repr__(self):
    return ''.join(["OwlTeam(id=", str(self.id), ",abbr=", self.abbr, ")"])
    
class OwlGame:
  def __init__(self, id, teams, winner, score):
    self.id = id
    self.teams = teams
    self.winner = winner
    self.score = score
  
  def __str__(self):
    return self.__repr__()
        
  def __repr__(self):
    return "".join(["OwlGame(id=", str(self.id), ",", self.teams[0].abbr, " ", str(self.score[0]), " ",
                    str(self.score[1]), " ", self.teams[1].abbr, ")"])
    
# Represents a match in OWL. Records teams, winner, and map score.
class OwlMatch:
  MatchResult = namedtuple("MatchResult", ["match_winner", "num_games", "winner_wins", "winner_losses", "winner_ties"])
  
  def __init__(self, id, date, teams, winner, games):
    self.id = id
    self.date = date
    self.teams = teams
    self.winner = winner
    self.games = games
    win, loss, draw = 0, 0, 0
    for game in games:
      if game.winner == self.winner:
        win += 1
      elif game.winner == None:
        draw += 1
      else:
        loss += 1
    self.result = OwlMatch.MatchResult(winner, len(games), win, loss, draw)
    
  def __str__(self):
    return self.__repr__()
    
  def __repr__(self):
    result = (self.result.winner_wins, self.result.winner_losses) if self.winner == self.teams[0] else \
             (self.result.winner_losses, self.result.winner_wins)
    return "".join(["OwlMatch(id=", str(self.id), ",", self.teams[0].abbr, " ", str(result[0]), " ",
                    str(result[1]), " ", self.teams[1].abbr, ",", str(self.date), ")"])

class OwlSchedule:
  def __init__(self):
    self.teams = {}
    self.matches = {}
    
  def AddMatch(self, match):
    competitors = match["competitors"]
    owl_competitors = [None, None]
    i = 0
    # Add competitors that haven't been seen before to the map.
    for competitor in competitors:
      key = competitor["id"]
      if key not in self.teams:
        self.teams[key] = OwlTeam(competitor["id"], competitor["name"], competitor["abbreviatedName"])
      owl_competitors[i] = self.teams[key]
      i += 1
      
    date = datetime.datetime.fromtimestamp(match["startDateTS"] / 1000.0)
    
    # Construct a list of games.
    games = []
    for game in match["games"]:
      points = game["points"]
      winner = None
      if points[0] > points[1]:
        winner = owl_competitors[0]
      elif points[0] < points[1]:
        winner = owl_competitors[1]
      games.append(OwlGame(game["id"], tuple(owl_competitors), winner, tuple(points)))

    owl_match = OwlMatch(match["id"], date, tuple(owl_competitors), self.teams[match["winner"]["id"]], games)
    self.matches[owl_match.id] = owl_match
  
  def __str__(self):
    return self.__repr__()
    
# Converts pythonified JSON from the OWL schedule API endpoint to python classes. Returns an
# instance of OwlSchedule.
class OwlScheduleBuilder:
  def BuildFromFile(file):
    with open(file, "r") as fin:
      return OwlScheduleBuilder.BuildFromJson(json.load(fin)) 

  def BuildFromApi(api):
    return OwlScheduleBuilder.BuildFromJson(api.Schedule())
    
  def BuildFromJson(json_schedule):
    stages = json_schedule["data"]["stages"]
    matches = []
    for stage in stages:
      if "Stage" in stage["name"]:
        for match in stage["matches"]:
          if match["state"] == "CONCLUDED":
            matches.append(match)
            
    schedule = OwlSchedule()
    matches.sort(key=OwlScheduleBuilder.GetMatchId)
    for match in matches:
      schedule.AddMatch(match)
    return schedule
    
  def GetMatchId(match):
    return match["id"]