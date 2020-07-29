""" Minesweeper WebSocket Server """
import re
from string import ascii_uppercase
from copy import deepcopy
import json
import asyncio
import websockets
from minesweeper import GameContext

LABEL = " " + ascii_uppercase

def parse_coord(input_str):
    """ parse coordinate string input """
    coord_temp = input_str
    coord_temp = coord_temp.replace("(", "")
    coord_temp = coord_temp.replace(")", "")
    coord_temp = coord_temp.split(",")
    if len(coord_temp) != 2:
        raise ValueError("invalid coordinates")
    coord = []
    for pos in coord_temp:
        # convert alphabetic coordinate to numerical coordinate
        # assuming ascii input
        if pos.isalpha():
            coord.append(ord(pos.upper()) - ord('A') + 1)
        else:
            coord.append(int(pos))

    return tuple(coord)

def print_game_context(game_context):
    """ print game state to terminal """
    game_context.render_gameboard()
    for x in range(0, game_context.max_x + 1):
        print(LABEL[x], end='')
    for y in range(1, game_context.max_y + 1):
        print()
        print(LABEL[y], end='')
        for x in range(1, game_context.max_x + 1):
            print(game_context.game_map[(x, y)], end="")
    print()

def jsonify_game_context(game_context):
    """ convert game context to a JSON compatible data structure """
    gc_dict = {}
    game_map_int = {}
    gc_dict["max_x"] = game_context.max_x
    gc_dict["max_y"] = game_context.max_y
    # cannot use map tuple keys in JSON
    # convert tuple key to integer based key
    for (x, y) in game_context.game_map:
        game_map_int[game_context.max_x * x + y] = game_context.game_map[(x, y)]

    gc_dict["game_map"] = game_map_int
    gc_dict["winning_condition"] = game_context.winning_condition()
    gc_dict["mines"] = len(game_context.mines)
    gc_dict["flags"] = len(game_context.flags)

    return json.dumps(gc_dict)

async def event_loop(websocket, path):
    """ event loop """

    print("websocket path:", path)
    game_context = GameContext()
    undo_list = []
    game_over = False

    while True:
        save_context = deepcopy(game_context)

        if not game_over:
            print_game_context(game_context)

        game_context_json = jsonify_game_context(game_context)

        print("Send...")
        await websocket.send(game_context_json)
        print("Wait...")
        recv = await websocket.recv()
        print("Recv...", recv)
        await asyncio.sleep(.25)

        command = recv

        if command == "":
            continue

        if command[0] == "!" and not game_over:
            try:
                coord_str = re.split(' |,', command, 1)[1]
                coord = parse_coord(coord_str)
            except ValueError:
                print("invalid input")
                continue

            undo_list.append(save_context)
            game_context.uncover_tile(coord)

            if game_context.hit_mine(coord):
                print("Game Over!")
                game_context.reveal = True
                game_over = True
                #game_context.uncover_tile(coord)
                game_context.visible.add(coord)
                game_context.render_gameboard()
                print_game_context(game_context)
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
                coord = {parse_coord(coord_str)}
                undo_list.append(save_context)
                game_context.set_flag(coord)
            except ValueError:
                print("invalid input")

        if command[0] == "%":
            print(game_context.mines)
            undo_list.append(save_context)
            game_context.reveal = not game_context.reveal

        if command[0] == "s":
            print("Restarting Game")
            undo_list = []
            game_context = GameContext()
            try:
                coord_str = re.split(' |,', command, 1)[1]
                coord = parse_coord(coord_str)
            except ValueError:
                print("invalid input")
                continue
            game_context.max_x = coord[0]
            game_context.max_y = coord[1]
            game_over = False

        if command[0] == "u":
            if undo_list:
                game_over = False
                game_context = undo_list.pop()
            else:
                print("Cannot undo")

# main
if __name__ == '__main__':
    print("Waiting for client connection...")
    server = websockets.serve(event_loop, 'localhost', 8081)
    asyncio.get_event_loop().run_until_complete(server)
    asyncio.get_event_loop().run_forever()
