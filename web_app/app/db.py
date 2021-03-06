import sqlite3
import time
import os 
import dill
import ast
import zlib
import sys

sys.path.append("../../DeflectiunCore")
from spaceshots_core.game import *

script_directory = os.path.dirname(os.path.abspath(__file__))
DATABASE = script_directory + "/sessions.db"
SESSIONS_DIR = script_directory + "/sessions/"
GAMES = {}

def reset_db():
    
    if os.path.isfile(DATABASE): os.remove(DATABASE)
    conn = sqlite3.connect(DATABASE)
    curr = conn.cursor()
    curr.execute("CREATE TABLE sessions (id varchar(5) PRIMARY KEY, scenes data, time float)")
    # curr.execute("PRAGMA cache_size=10000")
    conn.commit()
    conn.close()

def save_game_stupid(id, _game):
    GAMES.update({id : _game})

def save_game_pickle(id, _game):
    
    # packed = dill.dumps(_game, dill.HIGHEST_PROTOCOL)
    file = open(SESSIONS_DIR+id+".pkl", "wb")
    dill.dump(_game, file, protocol=dill.HIGHEST_PROTOCOL)
    file.close()         
    
def save_game_db(id, scenes):
    
    conn = sqlite3.connect(DATABASE)
    curr = conn.cursor()
    start = time.time()
    packed = dill.dumps(scenes, dill.HIGHEST_PROTOCOL)
    # print("> Bytes took", time.time()-start, "s")
    start = time.time()
           
    # Replace method
    try:
        curr.execute("REPLACE INTO sessions VALUES (?, ?, ?)", (id, packed, time.time()))    
    except:
        curr.execute("INSERT INTO sessions VALUES (?, ?, ?)", (id, packed, time.time()))      
    
    # print("> Write took", time.time()-start, "s")
        
    conn.commit()
    curr.close()
    conn.close()
    
def get_game_stupid(id):
    return GAMES[id]
    
def get_game_pickle(id):
    
    if not os.path.isfile(SESSIONS_DIR + id + ".pkl"):
        raise ValueError("Bitch game isn't even loaded.")
    
    file = open(SESSIONS_DIR+id+".pkl","rb")
    loaded = dill.load(file) 
    file.close()
    return loaded

def get_scene(id, level_i):

    conn = sqlite3.connect(DATABASE)
    curr = conn.cursor()
    
    # Load
    curr.execute("SELECT * FROM sessions WHERE id=?", (id,))
    
    try:
        scene = dill.loads(curr.fetchone()[1])[level_i]
        
        curr.close()
        conn.close()
        
        return scene
    
    except:
        # No scene found
        return None

def get_game_db(id):
     
    conn = sqlite3.connect(DATABASE)
    curr = conn.cursor()
    
    # Load
    curr.execute("SELECT * FROM sessions WHERE id=?", (id,))
    _game = dill.loads(curr.fetchone()[1])
    # _game = str_to_game(curr.fetchone()[1])
    
    curr.close()
    conn.close()
    
    return _game
    
def game_to_str(_game):
    
    return str(zlib.compress(dill.dumps(_game, dill.HIGHEST_PROTOCOL)))

def str_to_game(_str):
    
    return dill.loads(zlib.decompress(ast.literal_eval(_str)))
    