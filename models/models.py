from shared.db import db
from enum import Enum

class PlayerColor(Enum):
    BLACK = 'black'
    WHITE = 'white'

avoids=db.Table('avoids',db.metadata,
  db.Column('player_id',db.Integer,db.ForeignKey('players.id')),
  db.Column('avoids_id',db.Integer,db.ForeignKey('players.id'))
  )

class Club(db.Model):
  __tablename__="club"
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False, unique=True)
  players = db.relationship('Player', backref='club')

  def as_dict(self):
    return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}

class Player(db.Model):
  __tablename__="players"
  id = db.Column(db.Integer, primary_key=True)
  fName = db.Column(db.String,nullable=False)
  sName = db.Column(db.String,nullable=False)
  grade = db.Column(db.Integer, default=0)
  num_graded_games = db.Column(db.Integer, default = 0)
  active = db.Column(db.Boolean,default=True)
  playing = db.Column(db.Boolean,default=False)
  
  club_id = db.Column(db.Integer, db.ForeignKey('club.id'))
  

  games_as_white = db.relationship('Game', backref='white_player',lazy='joined', foreign_keys='Game.white_player_id')
  games_as_black = db.relationship('Game', backref='black_player',lazy='joined', foreign_keys='Game.black_player_id')

  _avoids = db.relationship('Player',
      secondary=avoids, 
      primaryjoin=(avoids.c.player_id==id), 
      secondaryjoin=(avoids.c.avoids_id==id),
      backref='avoided_by')

  def __repr__(self):
    return f"Player(id={self.id}, name={self.fName} {self.sName}, avoids={list(map(lambda x: x.fName+' '+x.sName, self.avoids))})"

  def as_dict(self):
    return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}


  @property
  def avoids(self):
    return self._avoids

  def add_to_avoids(self,player):
    if player not in self._avoids:
      self._avoids.append(player)
      player._avoids.append(self)

  def remove_from_avoids(self,player):
    if player in self._avoids:
      self._avoids.remove(player)
      player._avoids.remove(self)

class GameResult(Enum):
    ACTIVE='active'
    DRAW='draw'
    WHITE_WIN='white_win'
    BLACK_WIN='black_win'
  
class Game(db.Model):
  __tablename__="games"
  id=db.Column(db.Integer,primary_key=True)
  white_player_id = db.Column(db.Integer, db.ForeignKey('players.id'))
  black_player_id = db.Column(db.Integer, db.ForeignKey('players.id'))
  result=db.Column(db.Enum(GameResult),default=GameResult.ACTIVE)
  updated = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

  def __repr__(self):
    return f"Game(id={self.id}, white={self.white_player.fName} {self.white_player.sName}, black={self.black_player.fName} {self.black_player.sName}, result={self.result})"

  def as_dict(self):
    return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}

