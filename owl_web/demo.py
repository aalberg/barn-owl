import json
import urllib.request
from pprint import pprint
import sys

import data_input

owl_url = "https://api.overwatchleague.com/schedule"
output_file = "schedule2.json"

def dump_to_file(data):
  with open(output_file, "w") as fout:
    fout.write(data)
    #pprint(data, fout)

def get_match_id(match):
  return match["id"]
    
def main():
  # Retrieve JSON from Blizzard API.
  response = urllib.request.urlopen(owl_url)
  data = json.load(response)
  dump_to_file(json.dumps(data, indent=4, sort_keys=True))
  
  # Step through the JSON.
  stages = data["data"]["stages"]
  matches = []
  for stage in stages:
    if "Stage" in stage["name"]:
      for match in stage["matches"]:
        if match["state"] == "CONCLUDED":
          matches.append(match)
          
  matches.sort(key=get_match_id)
  for match in matches:
    competitors = match["competitors"]
    scores = match["wins"]
    print(competitors[0]["name"], scores[0], scores[1], competitors[1]["name"])
    
def main2():
  schedule = data_input.OwlScheduleBuilder.BuildFromFile("schedule2.json")
  print(len(schedule.teams), schedule.teams)
  print(len(schedule.matches), schedule.matches)
  print(schedule.matches[10223].games)

if __name__ == "__main__":
  if len(sys.argv) > 1 and sys.argv[1] == "2":
    main2()
  else:
    main()