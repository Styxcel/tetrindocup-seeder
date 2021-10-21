import numpy as np
import requests
from response import Response
import json
import pandas as pd
from datetime import datetime, date

# Player Name     -> /users/:user -> response.data.user.username
# TR              -> /users/:user -> response.data.user.rating
# Glicko          -> /users/:user -> response.data.user.glicko
# Max Rank        -> /news/user_{userID} -> repsonse.data.news.type = rankup && username = Player Name && rank = max
# VS              -> /users/:user -> response.data.user.vs
# Created Date    -> /users/:user -> response.data.user.ts

labels = ['discord', 'username', 'tr', 'glicko', 'rank', 'max rank', 'vs', 'created_date', 'not new acc']
rank_list = {
  'x': 1,
  'u': 2,
  'ss': 3,
  's+': 4,
  's': 5,
  's-': 6,
  'a+': 7,
  'a': 8,
  'a-': 9,
  'b+': 10,
  'b': 11,
  'b-': 12,
  'c+': 13,
  'c': 14,
  'c-': 15,
  'd+': 16,
  'd': 17
}
api = 'https://ch.tetr.io/api/'
user_api = api + 'users/{user}'
news_api = api + 'news/user_{user_id}'
idk = '???'

def get_payload(response):
  response = json.loads(response.text, object_hook=Response)
  if response.success == True:
    return response.data
  else:
    return None

def get_max_rank(id):
  response = requests.get(news_api.format(user_id = id))
  if response.ok == True:
    news = get_payload(response).news
    ranks = [feed.data.rank for feed in news if feed.type=='rankup']
    if len(ranks  ) > 0:
      return min(ranks, key=lambda rank: rank_list[rank])
    else:
      return '?'

def get_glicko(user):
  if(user.league.rank == 'z'):
    return user.league.glicko + user.league.rd
  else:
    return user.league.glicko

def clean_username(username):
  return username.strip()

def parse_date(date):
  format = "%Y-%m-%dT%H:%M:%S.%fZ"
  return datetime.strptime(date, format)

def get_player_data(username):
  username = clean_username(username)
  response = requests.get(user_api.format(user = username.lower()))
  try:
    if response.ok == True:
      user = get_payload(response).user
      return [user.username, user.league.rating, get_glicko(user), user.league.rank, get_max_rank(user._id), user.league.vs, parse_date(user.ts), (user.ts - date.today()).days > 30]
    else:
      return None
  except:
    return [idk, idk, idk, idk, idk, idk, idk]

def check_player_datas(path):
  players_raw_data = pd.read_csv(path, header=0)
  player_names = [name for name in players_raw_data['Nama di tetr.io'] if name is not np.nan]
  players_proc_data = pd.DataFrame([get_player_data(name) for name in player_names], columns = labels)
  players_proc_data.to_csv("output.csv")
  
players_xls_path = "responses.csv"

check_player_datas(players_xls_path)
