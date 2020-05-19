import sys
import math
sys.path.append("../../DeflectiunCore")

from spaceshots_core.game import *
from spaceshots_core.assests import *
from spaceshots_core.physics import * 
from spaceshots_core.scene import LevelBuilder, closest_dist_to_sc
from .db import *
from copy import deepcopy
import sys

FPS = 1000/90

def get_status(game):
    
    scene =  game.current_scene
    length, width = scene.size
    
    data = {
        "sc" : {
            "mass" : round(scene.sc.mass,2),
            "pos" : (round(scene.sc.x,2),round(scene.sc.y,2)),
            "speed" : round(scene.sc.vel.mag),
            "poly" : [[round(e,2) for e in i] for i in scene.sc.coords],
            "size" : (scene.sc.width, scene.sc.length),
            "rot" : round(scene.sc.theta,2),
            "gas_level" : scene.sc.gas_level,
            "min_dist_to_planet" : round(scene.sc.min_dist_to_planet,2),
            "gas_p_thrust" : scene.sc.gas_per_thrust,
            "i_gas_level" : scene.sc._initial_gas_level,
            "closest_dist_to_planet" : round(closest_dist_to_sc(scene.sc, scene.planets),1),
            "p" : [scene.sc.p.x, scene.sc.p.y],
            "thrust" : {
                "mag" : scene.sc.thrust_mag,
                "dir" : scene.sc.thrust_direction if scene.sc.thrust else "na",
                "on" : scene.sc.thrust
            }
        }
    }
    
    data.update({"n_planets" : len(scene.planets)})    
    for i,p in enumerate(scene.planets):
        p_data = {
            "pos": [round(i,2) for i in (p.x,p.y)],
            "mass" : round(p.mass,1),
            "radius" : round(p.radius,1),
            "orbit" : {
                "center" : [round(i,1) for i in (p.orbit.center_x, p.orbit.center_y)],
                "a" : round(p.orbit.a,1),
                "b" : round(p.orbit.b,1),
                "cw" : p.orbit.cw,
                "ang_step" : p.orbit.angular_step,
                "progress" : round(p.orbit.progress,2)
            }
        }
        data.update({"p" + str(i+1) : p_data})
    
    data.update({
        "scene" : {
            "size" : (length, width),
            "win_region" : [[round(i,1) for i in point] for point in scene.win_region],
            "win_vel" : scene.win_min_velocity,
            "attempts" : scene.attempts,
            "completion_score" : scene.completion_score,
            "attempt_reduction" : scene.attempt_score_reduction,
            "gas_bonus" : scene.gas_bonus_score,
            # "init_orbits" : scene.initial_orbit_pos
        }})
    
    return data

def status_to_game(status):
    
    status = dict(status)
    
    # Sc
    sc = Spacecraft('', status["sc"]["mass"], status["sc"]["gas_level"], status["sc"]["thrust"]["mag"], status["sc"]["size"][0], status["sc"]["size"][1], status["sc"]["gas_p_thrust"], status["sc"]["min_dist_to_planet"])
    sc.p = Momentum(status["sc"]["p"][0],status["sc"]["p"][1])
    sc.gas_level = status["sc"]["gas_level"]
    
    # Planets
    planets = []
    for i in range(status["n_planets"]):
        p = status["p"+str(i+1)]
        o = Orbit(p["orbit"]["a"], p["orbit"]["b"], p["orbit"]["center"][0], p["orbit"]["center"][1], CW=p["orbit"]["cw"])
        o.angular_step = p["orbit"]["ang_step"]
        planet = Planet("", p["mass"], orbit=o, radius_per_kilogram=p['radius']/p["mass"])
        planet.orbit.progress = p["orbit"]["progress"]
        planet.x, planet.y = p["pos"]
        planet.make_poly()
        planets.append(planet)
    
    # Scene    
    scene = Scene(status["scene"]["size"], sc, planets, status["sc"]["pos"], status["scene"]["win_region"], status["scene"]["win_vel"], status["scene"]["completion_score"], status["scene"]["attempt_reduction"], status["scene"]["gas_bonus"], reset=False)    
    scene.attempts = status["scene"]["attempts"]
    scene.won, scene.fail = status["won"], status["fail"]
    scene.initial_orbit_pos = status["init_orbits"]
    scene.sc_start_pos = status["sc_start_pos"]
    
    return Game(FPS, [scene], reset=False)

def step(prev_status, cmd):
    
    # print("--------------------")
    start = time.time()
    # _game = str_to_game(game_str)
    # _game = get_game_stupid(id)
    _game = status_to_game(prev_status)
    # print("str to game took", time.time()-start, "s")
    won, fail, message = _game.step(cmd)
    # start = time.time()
    # bytes_str = game_to_str(_game)
    # save_game_stupid(id, _game)
    # print("game to str took", time.time()-start, "s")
    status = get_status(_game)
    status.update({
        "won" : won,
        "fail" : fail,
        "message" : message,
        # "bytes" : bytes_str
    })

    return status

def load_game(id):
    # global original
    _game = Game(scenes=[builder.create("easy") for i in range(1)], fps=FPS)
    # print(_game.scenes[0].planets[0].orbit.angular_step)
    # save_game_stupid(id, _game)
    # original = game_to_str(_game)
    status = get_status(_game)
    status.update({
        "won" : False,
        "fail" : False,
        "message" : "",
        "init_orbits" : _game.scenes[0].initial_orbit_pos,
        "sc_start_pos" : _game.scenes[0].sc_start_pos,
        # "bytes" : original
    })
    return status
    
screen_x, screen_y = 900, 700
builder = LevelBuilder(screen_x, screen_y)
original = ""