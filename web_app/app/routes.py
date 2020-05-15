import os
import json
from app import app
from flask import render_template, request
from .game import *
import numpy as np
from flask_socketio import emit

# Load sprites 
images_path = os.path.abspath("app/static/images/ship2")
imgs = []
for i in os.listdir(images_path):
    path = os.path.join(images_path, i)
    imgs.append({
        "src" : "static/images/ship2/"+i,
        "name" : i.replace(".png", "")
    })

@app.route('/')
@app.route('/index')
def index():    
    return render_template('index.html', planets = scene.planets, images=imgs, logo="draft1.png")

@app.route('/get/<cmd>')
def get(cmd):
    cmd = int(cmd)
    status = step(cmd)
    return json.dumps(status)

@app.route('/load/')
def load():
    return json.dumps(load_game())

# @socketio.on('my event')
# def test_message(message):
#     emit('my response', {'data': message['data']})
    
# @socketio.on('connect')
# def test_connect():
#     emit('my response', {'data': 'Connected'})