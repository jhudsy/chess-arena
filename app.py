import os,io,traceback,json,logging
import csv
import networkx as nx
from flask import Flask, request, redirect, url_for, flash,render_template, jsonify
from werkzeug.utils import secure_filename

from shared.db import db
from models.models import Player,Game,GameResult,Club

app = Flask(__name__, static_url_path='/static')
app.logger.setLevel(logging.INFO)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db.init_app(app)
with app.app_context():
  db.create_all()


@app.route("/")
def hello_world():
  return render_template("header.html")


################################################################
#Utility function - given a set of round numbers, find the lowest number not in there, starting at 1
def find_min_absent(s):
  i=1
  while i in s:
    i+=1
  return i

@app.route("/crosstable")
def cross_table():

  player_games={}
  player_min_round_number={}
  player_points={}
  player_numgames_played={}
  for p in Player.query.all():
    player_points[p]=0
    player_numgames_played[p]=0
    player_games[p]=[]
    player_min_round_number[p]=set([])
  
  for g in Game.query.order_by(Game.updated.desc()).all():
    if g.result!=GameResult.ACTIVE:
      pw=g.white_player
      pb=g.black_player
      player_numgames_played[pw]+=1
      player_numgames_played[pb]+=1
      
      round_number=find_min_absent(player_min_round_number[pw].union(player_min_round_number[pb]))
      player_min_round_number[pw].add(round_number)
      player_min_round_number[pb].add(round_number)
      
      if g.result==GameResult.WHITE_WIN:
        player_points[pw]+=1
        player_games[pw].append(f"({round_number}){pb.id}w+")
        player_games[pb].append(f"({round_number}){pw.id}b-")
      if g.result==GameResult.BLACK_WIN:
        player_points[pb]+=1
        player_games[pw].append(f"({round_number}){pb.id}w-")
        player_games[pb].append(f"({round_number}){pw.id}b+")
      if g.result==GameResult.DRAW:
        player_points[pw]+=0.5
        player_points[pb]+=0.5
        player_games[pw].append(f"({round_number}){pb.id}w=")
        player_games[pb].append(f"({round_number}){pw.id}b=")
  
  ct=[]
  for p in Player.query.order_by(Player.id).all():
    row={}
    row["fName"]=p.fName
    row["sName"]=p.sName
    row["id"]=p.id
    row["numGamesPlayed"]=player_numgames_played[p]
    row["points"]=player_points[p]
    row["percent"]=0.0 if row["numGamesPlayed"]==0 else row["points"]/row["numGamesPlayed"]
    row["games"]=player_games[p]
    ct.append(row)
  
  return jsonify(ct)
    
################################################################
@app.route("/matchings")
def get_matchings():
  app.logger.info("starting matching")
  active_players=Player.query.filter((Player.active==True) & (Player.playing==False)).all()
  g=nx.Graph()
  for a in active_players:
    g.add_node(a)
    for b in active_players:
      if a!=b and (a,b) not in g.edges(a):
        #calculate edge weight based on
        #if players had played each other before
        #if players are in the avoid list of each other
        #if one player has a grade and the other doesn't, preferring players near 8 graded games
        #grade difference
        #win performance difference
        #color they should play
        
        #number of times the two players have played before
        #OPTIMIZED
        num_played_before=0
        for gm in a.games_as_white:
          if gm.black_player==b:
             num_played_before+=1
        for gm in a.games_as_black:
          if gm.white_player==b:
             num_played_before+=1

        #SLOW
        #num_played_before=db.session.query(((Game.white_player==a) & (Game.black_player==b)) | ((Game.white_player==b) & (Game.black_player==a))).count()

        #are they in the avoid list for each other
        in_avoid_list= 1 if b in a.avoids else 0

        #do either need/does this provide a graded game
        grading_needed_pairing = min(1+a.num_graded_games,1+b.num_graded_games) if (a.num_graded_games>=8 and b.num_graded_games<8) or (b.num_graded_games>=8 and a.num_graded_games<8) else 0

        #what is the win performance for the players
        #OPTIMIZED
        win_performance_a=0
        win_performance_b=0
        for gm in a.games_as_white:
          if gm.result==GameResult.WHITE_WIN:
             win_performance_a+=2
          elif gm.result==GameResult.DRAW:
             win_performance_a+=1
        for gm in a.games_as_black:
          if gm.result==GameResult.BLACK_WIN:
             win_performance_a+=2
          elif gm.result==GameResult.DRAW:
             win_performance_a+=1

        for gm in b.games_as_white:
          if gm.result==GameResult.WHITE_WIN:
             win_performance_b+=2
          elif gm.result==GameResult.DRAW:
             win_performance_b+=1
        for gm in b.games_as_black:
          if gm.result==GameResult.BLACK_WIN:
             win_performance_b+=2
          elif gm.result==GameResult.DRAW:
             win_performance_b+=1

        #SLOW
        #win_performance_a=2*(db.session.query((Game.white_player==a) & (Game.result==GameResult.WHITE_WIN)).count() + db.session.query((Game.black_player==a) & (Game.result==GameResult.BLACK_WIN)).count()) + (db.session.query(((Game.white_player==a) | (Game.black_player==a)) & (Game.result==GameResult.DRAW)).count())
        #win_performance_b=2*(db.session.query((Game.white_player==b) & (Game.result==GameResult.WHITE_WIN)).count() + db.session.query((Game.black_player==b) & (Game.result==GameResult.BLACK_WIN)).count()) + (db.session.query(((Game.white_player==b) | (Game.black_player==b)) & (Game.result==GameResult.DRAW)).count())

        #grade difference for the two players
        grade_difference=abs(a.grade-b.grade)

        same_club=0
        if a.club!=None and b.club!=None and (a.club==b.club):
          same_club=1

        weight=num_played_before*config["weight_num_played_before"]+ in_avoid_list*config["weight_in_avoid_list"]+ grading_needed_pairing*config["weight_grading_needed_pairings"]+ abs(win_performance_a-win_performance_b)*config["weight_win_performance"]+ grade_difference*config["weight_grade_difference"]+same_club*config["weight_same_club"]
	
        if (in_avoid_list==0 or not config["hard_avoids"]==1) and (same_club==0 or not config["hard_avoid_club"]==1):
          g.add_edge(a,b,weight=weight)
  
  app.logger.info("finishing db")
  matching=nx.max_weight_matching(g,maxcardinality=True) #we now have pairs of players
  app.logger.info("finishing matching")
  ret=[]
  for m in matching:
    a=m[0]
    b=m[1]
    if len(a.games_as_white)/(1+len(a.games_as_white)+len(a.games_as_black))>len(b.games_as_white)/(1+len(b.games_as_white)+len(b.games_as_black)):
      ret.append((b.id,a.id))
    else:
      ret.append((a.id,b.id))
  app.logger.info("sending data")
  return jsonify(ret)

################################################################
@app.route("/games/<int:active>")
def get_all_games(active):
  if active==1:
    return jsonify(list(map(lambda x: x.as_dict(),Game.query.order_by(Game.updated).filter(Game.result==GameResult.ACTIVE).all())))
  if active==0:
    return jsonify(list(map(lambda x: x.as_dict(),Game.query.order_by(Game.updated).filter(Game.result!=GameResult.ACTIVE).all())))
################################################################

@app.route("/games/<int:id>/<int:active>")
def get_games(id,active):
  if active==1:
    return jsonify(list(map(lambda x: x.as_dict(),Game.query.order_by(Game.updated).filter(((Game.white_player==Player.query.get(id)) | (Game.black_player==Player.query.get(id))) & (Game.result==GameResult.ACTIVE)).all())))
  else:
    return jsonify(list(map(lambda x: x.as_dict(),Game.query.order_by(Game.updated).filter(((Game.white_player==Player.query.get(id)) | (Game.black_player==Player.query.get(id))) & (Game.result!=GameResult.ACTIVE)).all())))
  
################################################################
@app.route("/game/<int:id>",methods=['DELETE'])
def delete_game(id):
  g=Game.query.get(id)
  if g.result!=GameResult.ACTIVE:
    if g.white_player.grade>0 and g.white_player.num_graded_games>=8:
      g.black_player.num_graded_games-=1
    if g.black_player.grade>0 and g.black_player.num_graded_games>=8:
      g.white_player.num_graded_games-=1
  if g.result==GameResult.ACTIVE:
    g.black_player.playing=False
    g.white_player.playing=False
  db.session.delete(g)
  db.session.commit()
  return jsonify(success=True)
################################################################
@app.route("/game/<int:id>/<result>")
def update_game_result(id,result):
  result=GameResult(result)
  g=Game.query.get(id)
  g.white_player.playing=False
  g.black_player.playing=False
  #only update number of graded games if we are moving from active
  if g.result==GameResult.ACTIVE and result!=GameResult.ACTIVE:
    if g.white_player.grade>0 and g.white_player.num_graded_games>=8:
      g.black_player.num_graded_games+=1
    if g.black_player.grade>0 and g.black_player.num_graded_games>=8:
      g.white_player.num_graded_games+=1
  #if we are moving back to active, decrease games as needed
  if g.result!=GameResult.ACTIVE and result==GameResult.ACTIVE:
    if g.white_player.grade>0 and g.white_player.num_graded_games>=8:
      g.black_player.num_graded_games-=1
    if g.black_player.grade>0 and g.black_player.num_graded_games>=8:
      g.white_player.num_graded_games-=1
  g.result=result
  db.session.commit()
  return jsonify(success=True)
################################################################
@app.route("/game/<int:wid>/<int:bid>",methods=['POST'])
def create_game(wid,bid):
  g=Game()
  g.white_player=Player.query.get(wid)
  g.black_player=Player.query.get(bid)
  g.result=GameResult.ACTIVE
  g.white_player.playing=True
  g.black_player.playing=True
  db.session.add(g)
  db.session.commit()
  return jsonify(success=True)
################################################################
@app.route("/player/<int:id>",methods=['DELETE'])
def delete_player(id): #TODO: don't forget to delete games
  try:
    p=Player.query.get(id)
    for p2 in p.avoids:
      p.remove_from_avoids(p2)
    db.session.delete(p)
    db.session.commit()
    return jsonify(success=True)
  except Exception as e:
    print(e)
    traceback.print_exc()
    return jsonify(success=False),400
################################################################
@app.route("/player",methods=['POST'])
def create_player():
  try:
    data=request.get_json()
    print(data)
    p=Player()
    p.fName=data["fName"]
    p.sName=data["sName"]
    p.grade=int(data["grade"])
    p.num_graded_games=int(data["num_graded_games"])
    p.playing=False
    p.active=data["active"]
    p.club=None
    if int(data["club"])!=-1:
      p.club=Club.query.get(data["club"])

    #no need to remove avoids as new player should have no avoids
    for v in data["avoids"]:
      p.add_to_avoids(Player.query.get(v))
    db.session.add(p)
    db.session.commit()
    return jsonify(success=True)
  except Exception as e:
    print(e)
    traceback.print_exc()
    return jsonify(success=False),400
################################################################
@app.route("/player/<int:id>",methods=['PUT'])
def update_player(id):
  try:
    data=request.get_json()
    p=Player.query.get(id)
    p.fName=data["fName"]
    p.sName=data["sName"]
    p.grade=int(data["grade"])
    p.num_graded_games=int(data["num_graded_games"])
    #p.playing=data["playing"]
    p.active=data["active"]
    p.club=None
    if int(data["club"])!=-1:
      p.club=Club.query.get(int(data["club"]))

    a=p.avoids
    for v in a:
      p.remove_from_avoids(v)
    for v in data["avoids"]:
      p.add_to_avoids(Player.query.get(int(v)))
    db.session.commit()
    return jsonify(success=True)
  except Exception as e:
    print(e)
    traceback.print_exc()
    return jsonify(success=False),400
################################################################
@app.route("/player_summary/<int:id>",methods=['GET'])
def get_player_summary(id):
  p=Player.query.get(id)
  d=Player.query.get(id).as_dict()
  d["num_games"]=len(p.games_as_white)+len(p.games_as_black)
  num_win=0
  num_draw=0
  num_lost=0
  
  opp_rating=0

  game_summary=[]
  for g in p.games_as_white:
    opp_rating+=g.black_player.grade
    outcome=""
    if g.result==GameResult.WHITE_WIN:
       outcome="+"
       num_win+=1
    elif g.result==GameResult.DRAW:
       outcome="="
       num_draw+=1
    else:
       outcome="-"
       num_lost+=1
    game_summary.append((g.updated,(p.id,f"{p.fName} {p.sName}",g.black_player.id,f"{g.black_player.fName} {g.black_player.sName}",outcome)))
  for g in p.games_as_black:
    opp_rating+=g.white_player.grade
    outcome=""
    if g.result==GameResult.BLACK_WIN:
       outcome="+"
       num_win+=1
    elif g.result==GameResult.DRAW:
       outcome="="
       num_draw+=1
    else:
       outcome="-"
       num_lost+=1
    game_summary.append((g.updated,(g.white_player.id,f"{g.white_player.fName} {g.white_player.sName}",p.id,f"{p.fName} {p.sName}",outcome)))
  game_summary.sort(key=lambda x: x[0],reverse=True)
  d["games"]=game_summary
  d["num_win"]=num_win
  d["num_draw"]=num_draw
  d["num_lost"]=num_lost
  tot_games=num_draw+num_win+num_lost
  d["performance_rating"]=0
  if tot_games!=0:
    #calculate performance rating as per wikipedia page
    d["performance_rating"]=(opp_rating/tot_games)+800*(d["num_win"]+0.5*d["num_draw"])/tot_games-400

  d["avoids"]=[]
  for a in p.avoids:
    d["avoids"].append(a.fName+" "+a.sName)
    d["avoids"].sort()
  if p.club!=None:  
    d["club"]=p.club.name
  else:
    d["club"]="(None)"
  return jsonify(d)
    
  
 
################################################################
@app.route("/player/<int:id>",methods=['GET'])
def get_player(id):
  avoids=[]
  for p in Player.query.get(id).avoids:
    avoids.append(p.id)

  d=Player.query.get(id).as_dict()
  d["avoids"]=avoids
  
  g=[]
  for gm in Game.query.filter(Game.white_player==Player.query.get(id) or Game.black_player==Player.query.get(id)).order_by(Game.updated.desc()).all():
    g.append(gm.id)
  d["games"]=g
  #if p.club!=None:
  #  print(f"in get, player is {p}, club is {p.club} id is {p.club.id}")
  #  d["club_id"]=p.club.id
  #else:
  #  d["club_id"]=-1
  
  
  return jsonify(d)
  #return jsonify(Player.query.get(id).as_dict())
################################################################
@app.route("/players")
def player_list():
  return jsonify(list(map(lambda x: x.as_dict(),Player.query.order_by(Player.fName, Player.sName).all())))
################################################################
@app.route("/club/<int:id>",methods=['DELETE'])
def delete_club(id):
  c=Club.query.get(id)
  for p in c.players:
    p.club=None
  db.session.delete(c)
  db.session.commit()
  return jsonify(success=True)
################################################################
@app.route("/club/<int:id>",methods=['PUT'])
def update_club(id):
  data=request.get_json()
  c=Club.query.get(id)
  c.name=data["name"]
  db.session.commit()
  return jsonify(success=True)

################################################################
@app.route("/club/",methods=['POST'])
def create_club():
  data=request.get_json()
  c=Club()
  c.name=data["name"]
  db.session.add(c)
  db.session.commit()
  return jsonify(success=True)
  
################################################################
@app.route("/club/<int:id>",methods=['GET'])
def get_club(id):
  return jsonify(Club.query.get(id).name)
################################################################
@app.route("/clubs")
def club_list():
  return jsonify(list(map(lambda x: x.as_dict(),Club.query.order_by(Club.name).all())))

################################################################
@app.route("/players_to_match")
def get_free_players():
  return jsonify(list(map(lambda x: x.as_dict(),Player.query.order_by(Player.fName, Player.sName).filter((Player.active==True) & (Player.playing==False)).all())))
################################################################
# CSV should be id,fName,sName,grade, num_rated_games_played,avoidlistIDs...

@app.route("/upload",methods=['POST','GET'])
def upload_playerlist():
  if request.method == 'GET':
    return render_template('upload.html')
  if 'file' not in request.files:
    return jsonify({'error':'no file present'}),400
  file = request.files['file']
  if file.filename == '':
    return jsonify({'error':'no file present'}),400

  try:
    csv_reader=csv.reader(io.TextIOWrapper(file), delimiter=',')
    players={}
    avoids={}
    Player.query.delete()
    Game.query.delete()
    Club.query.delete()
    for row in csv_reader:
      p=Player()
      p.fName=row[1]
      p.sName=row[2]
 
      #handle auto club creation
      club=row[3]
      p.club=None
      if club.strip()!="":
        c=Club.query.filter(Club.name==club).first()
        if not c:
          c=Club()
          c.name=club
          db.session.add(c)
          db.session.commit()

        c=Club.query.filter(Club.name==club).first()
        p.club=c
        
      p.grade=int(row[4])
      p.num_graded_games=int(row[5])
      p.active=True
      p.playing=False
      players[row[0]]=p
      avoids[row[0]]=tuple(row[6:])
    for i in players:
      for j in avoids[i]:
        players[i].add_to_avoids(players[j])
      db.session.add(players[i])
    db.session.commit()
    return jsonify(success=True)
  except Exception as e:
    print(e)
    traceback.print_exc()
    return jsonify({'error':'failed to read file'}),400
################################################################
config = {}

# Load the initial configuration from the JSON file
def load_config():
    global config
    with open('config.json') as file:
        config = json.load(file)

# Save the updated configuration to the JSON file
def save_config():
    with open('config.json', 'w') as file:
        json.dump(config, file, indent=4)

# Route to handle updating the configuration via web form
@app.route('/config', methods=['GET', 'POST'])
def config():
    global config

    if request.method == 'POST':
        # Update the configuration based on form input
        data=request.get_json()
        config=data

        # Save the updated configuration
        save_config()
        return jsonify(success=True)
    else:
        return jsonify(config)

load_config()
print("loaded config")
