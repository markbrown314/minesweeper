"""
Minesweeper

Implementation of the game Minesweeper as defined here: 
https://rosettacode.org/wiki/Minesweeper_game

Implemented with tuple sets
TODO: probably better as object
"""
from random import randint, seed
import re

MAX_X = 8
MAX_Y = 8
MAX_MINES = 1
PERCENT_MINES = .25
RAND_SEED = 1

def adjecency_check(input_set, coord, match = True):
    for x in range(coord[0]-1, coord[0]+2):
        for y in range(coord[1]-1, coord[1]+2):
            if (x,y) == coord:
                continue
            if match and (x,y) in input_set:
                yield(x,y)
            if not match and (x,y) in input_set:
                yield(x,y)

def adjecent_mines(board, coord):
    mine_count = 0
    for coord in adjecency_check(board["mines"], coord):
        mine_count += 1
    return mine_count

def uncover_tile(board, coord):

    if coord in board["visible"]:
        return

    if adjecent_mines(board, coord) > 0:
        board["visible"].add(coord)
        return

    if coord in board["empty"]:
        board["visible"].add(coord)

    for pos in adjecency_check(board["empty"], coord):
        uncover_tile(board, pos)
        
def render_gameboard(board):
    char = "^"
    for y in range(1, MAX_Y + 1):
        print()
        for x in range(1, MAX_X + 1):
            if (x,y) in board["flags"]:
                char = "?"
            elif (x,y) not in board["visible"]:
                char = "#"
            else:
                mine_count = adjecent_mines(board, (x,y))
                if mine_count == 0:
                    char = "."
                else:
                    char = str(mine_count)

            if board["reveal"] and (x,y) in board["mines"]:
                char = "*"

            print(char, end="")
    print()

def parse_coord(input_str):
    coord_temp = input_str
    coord_temp = coord_temp.replace("(", "")
    coord_temp = coord_temp.replace(")", "")
    coord_temp = coord_temp.split(",")
    if len(coord_temp) != 2:
        raise ValueError("invalid coordinates")
    coord = []
    for pos in coord_temp:
        coord.append(int(pos))
    return tuple(coord)

def default_mine_placement(board):
    # layout mines: random placement
    seed(board["rand_seed"])

    while True:
        if len(board["mines"]) == board["max_mines"]:
            break
        mine_coord = (randint(1, board["max_x"]), randint(1, board["max_y"]))
        if mine_coord in board["mines"]:
            continue
        board["mines"].add(mine_coord)
    print(board["mines"])


def init_gameboard(**kwargs):
    board = {}

    # defaults
    board["rand_seed"] = RAND_SEED
    board["max_x"] = MAX_X
    board["max_y"] = MAX_Y
    board["percent_mines"] = PERCENT_MINES
    board["max_mines"] = MAX_MINES
    board["layout_callback"] = default_mine_placement
    
    board["mines"] = set()
    board["flags"] = set()
    board["visible"] = set()

    # process kwarg overrides
    params = {"max_x", "max_y", "percent_mines", "max_mines", "layout_callback"}
    for key in kwargs:
        if key in params:
            board[key] = kwargs[key]
        else:
            raise ValueError("invalid argument: " + key)

     # check settings for too many mines
    total_tiles = board["max_x"] * board["max_y"]
    check_percent_mines = board["max_mines"] / total_tiles
    assert check_percent_mines < board["percent_mines"]

    board["empty"] = set()

    for y in range(1, board["max_y"] + 1):
        for x in range(1, board["max_x"] + 1):
            if not (x,y) in board["mines"]:
                board["empty"].add((x,y))

    board["reveal"] = False

    # layout mines
    board["layout_callback"](board)

    return board

def eventloop(board, **kwargs):
    input_callback = input
    render_callback = render_gameboard
    
    for key in kwargs.items():
        if key == "input_callback":
            input_callback = kwargs[key]
        elif key == "render_callback":
            render_callback = kwargs[key]
        else:
            raise ValueError("invalid argument: " + key)
    while True:
        # check winning condition
        if not board["visible"] ^ board["empty"] - board["mines"]:
            print("You Win!!!")
            board["reveal"] = True
            render_gameboard(board)
            return

        render_callback(board)
        command = input_callback(":")
        if command == "":
            continue

        if command == "quit":
            return

        if command[0] == "!":
            try:
                coord_str = re.split(' |,', command, 1)[1]
                coord = parse_coord(coord_str)
                if coord in board["mines"]:
                    print("Game Over!")
                    board["reveal"] = True
                    render_callback(board)
                    return
                uncover_tile(board, coord)
            except:
                print("invalid input")

        if command[0] == "?":
            try:
                coord_str = re.split(' |,', command, 1)[1]
                coord = parse_coord(coord_str)
                board["flags"].add(coord)
            except:
                print("invalid input")

        if command == "%":
            board["reveal"] = not board["reveal"]

def main():
    eventloop(init_gameboard())

if __name__ == "__main__":
    main()