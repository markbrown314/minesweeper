""" Minesweeper WebSocket Server """
import re
from copy import deepcopy
import json
import asyncio
import websockets
from minesweeper import GameContext
from time import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import os

def parse_tuple(input_str):
    """ parse coordinate string input """
    tuple_temp = input_str
    tuple_temp = tuple_temp.replace("(", "")
    tuple_temp = tuple_temp.replace(")", "")
    tuple_temp = tuple_temp.split(",")
    if len(tuple_temp) < 1:
        raise ValueError("invalid tuple")

    return tuple([int(value) for value in tuple_temp])


def jsonify_game_context(game_context):
    """ convert game context to a JSON compatible data structure """
    game_context_dict = {}
    game_context_dict["rand_seed"] = game_context.rand_seed
    game_context_dict["max_x"] = game_context.max_x
    game_context_dict["max_y"] = game_context.max_y
    game_context_dict["percent_mines"] = game_context.percent_mines
    game_context_dict["max_mines"] = game_context.max_mines
    game_context_dict["mines"] = list(game_context.mines)
    game_context_dict["flags"] = list(game_context.flags)
    game_context_dict["visible"] = list(game_context.visible)
    game_context_dict["empty"] = list(game_context.empty)

    game_context_dict["game_map"] = {}

    for (x, y) in game_context.game_map:
        game_context_dict["game_map"][str(x) + "," + str(y)] = game_context.game_map[(x, y)]

    game_context_dict["winning_condition"] = game_context.winning_condition()
    game_context_dict["loosing_condition"] = game_context.loosing_condition()

    return json.dumps(game_context_dict)

def dejsonify_game_context(json_game_context):
    """ convert game context to a JSON compatible data structure """
    game_context = GameContext()
    #print(json_game_context)
    game_context_dict = json.loads(json_game_context)

    game_context.rand_seed = game_context_dict["rand_seed"]
    game_context.max_x = game_context_dict["max_x"]
    game_context.max_y = game_context_dict["max_y"]
    game_context.percent_mines = game_context_dict["percent_mines"]
    game_context.max_mines = game_context_dict["max_mines"]
    game_context.mines = { tuple(t) for t in game_context_dict["mines"] }
    game_context.flags = { tuple(t) for t in game_context_dict["flags"] }
    game_context.visible = { tuple(t) for t in game_context_dict["visible"] }
    game_context.empty = { tuple(t) for t in game_context_dict["empty"] }

    for c in game_context_dict["game_map"]:
        j = c.split(",")
        x = int(j[0])
        y = int(j[1])
        game_context.game_map[(x,y)] = game_context_dict["game_map"][c]

    game_context.command = game_context_dict["command"]

    return game_context

async def event_loop(websocket, path):
    """ event loop """

    print("websocket path:", path)
    game_context = GameContext()
    game_over = False

    while True:
        if not game_over:
            game_context.render_gameboard()

        game_context_json = jsonify_game_context(game_context)

        t1 = time()
        print("Send...")
        await websocket.send(game_context_json)
        t2 = time()
        print("delta time:", t2 - t1)

        print("Wait...")
        recv = await websocket.recv()
        print("Recv...", recv)
        await asyncio.sleep(.25)

        game_context_json = recv
        #print(game_context_json)
        game_context = dejsonify_game_context(game_context_json)
        command = game_context.command

        if command == "":
            continue

        if command[0] == "!" and not game_over:
            try:
                coord_str = re.split(' |,', command, 1)[1]
                coord = parse_tuple(coord_str)
            except ValueError:
                print("invalid input")
                continue
            if not (coord in game_context.visible):
                game_context.uncover_tile(coord)

            print("delta time:", t2 - t1)

            if game_context.hit_mine(coord):
                print("Game Over!")
                game_over = True
                game_context.visible.add(coord)
                game_context.render_gameboard()
                continue

            # check winning condition
            if game_context.winning_condition():
                game_context.reveal = True
                game_context.render_gameboard()
                game_over = True
                print("You Win!!!")
                continue

        if command[0] == "?" and not game_over:
            try:
                coord_str = re.split(' |,', command, 1)[1]
                coord = {parse_tuple(coord_str)}
                game_context.set_flag(coord)
            except ValueError:
                print("invalid input")

        if command[0] == "%":
            print(game_context.mines)
            game_context.reveal = not game_context.reveal

        if command[0] == "s":
            print("Restarting Game")
            game_context = GameContext()
            try:
                tuple_str = re.split(' |,', command, 1)[1]
                restart_tuple = parse_tuple(tuple_str)
            except ValueError:
                print("invalid input")
                continue
            game_context.max_x = restart_tuple[0]
            game_context.max_y = restart_tuple[1]
            game_context.max_mines = restart_tuple[2]
            game_over = False

        if command[0] == "u":
                print("Cannot undo")
# main

def webserver():
    os.chdir("public/")
    print("Setting up Webserver...")
    http_server = HTTPServer(('', 8000), SimpleHTTPRequestHandler)
    http_server.serve_forever()

if __name__ == '__main__':
    # launch webserver
    threading.Thread(target=webserver, daemon=True).start()
    print("Waiting for client connection...")
    server = websockets.serve(event_loop, 'localhost', 8081)
    asyncio.get_event_loop().run_until_complete(server)
    asyncio.get_event_loop().run_forever()
