"""
Minesweeper

Implementation of the game Minesweeper as defined here:
https://rosettacode.org/wiki/Minesweeper_game

by Mark Brown <mark.brown314@gmail.com>
"""
from random import randint, seed
import re
import string

MAX_X = 10
MAX_Y = 10
MAX_MINES = 10
PERCENT_MINES = .25
RAND_SEED = 1
LABEL = " " + string.ascii_uppercase

def adjecency_check(input_set, coord, match=True):
    for x in range(coord[0]-1, coord[0]+2):
        for y in range(coord[1]-1, coord[1]+2):
            if (x, y) == coord:
                continue
            if match and (x, y) in input_set:
                yield(x, y)
            if not match and (x, y) not in input_set:
                yield(x, y)

def adjecent_mines(board, coord):
    return len([*adjecency_check(board["mines"], coord)])

def uncover_tile(board, coord):

    if coord in board["visible"]:
        return

    # first move init board
    if not board["visible"]:
        board["layout_callback"](board, coord)      

    if adjecent_mines(board, coord) > 0:
        board["visible"].add(coord)
        return

    if coord in board["empty"]:
        board["visible"].add(coord)

    for pos in adjecency_check(board["empty"], coord):
        uncover_tile(board, pos)

def render_gameboard(board):
    char = "^"
    for x in range(0, MAX_X + 1):
        print(LABEL[x], end='')
    for y in range(1, MAX_Y + 1):
        print()
        print(LABEL[y], end='')
        for x in range(1, MAX_X + 1):
            if (x, y) in board["flags"]:
                char = "?"
            elif (x, y) not in board["visible"]:
                char = "#"
            else:
                mine_count = adjecent_mines(board, (x, y))
                if mine_count == 0:
                    char = "."
                else:
                    char = str(mine_count)

            if board["reveal"] and (x, y) in board["mines"]:
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
        # convert alphabetic coordinate to numerical coordinate
        # assuming ascii input
        if pos.isalpha():
            coord.append(ord(pos.upper()) - ord('A') + 1)
        else:
            coord.append(int(pos))

    return tuple(coord)

def default_mine_placement(board, initial_coord=None):
    # layout mines: random placement
    seed(board["rand_seed"])
    exclude_map = set(board["mines"])
    exclude_map.update([*adjecency_check(set(), initial_coord, False)])
    exclude_map.update([initial_coord])

    while True:
        if len(board["mines"]) >= board["max_mines"]:
            break
        mine_coord = (randint(1, board["max_x"]), randint(1, board["max_y"]))
        if mine_coord in exclude_map:
            continue
        board["mines"].add(mine_coord)
        exclude_map.add(mine_coord)

    for y in range(1, board["max_y"] + 1):
        for x in range(1, board["max_x"] + 1):
            if not (x, y) in board["mines"]:
                board["empty"].add((x, y))

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
    assert check_percent_mines <= board["percent_mines"]

    board["empty"] = set()

    board["reveal"] = False

    return board

def eventloop(board):
    input_callback = input
    render_callback = render_gameboard

    while True:
        # check winning condition
        """
        if not board["visible"] ^ board["empty"] - board["mines"]:
            print("You Win!!!")
            board["reveal"] = True
            render_callback(board)
            return
        """

        render_callback(board)
        command = input_callback("command (h for help):")
        if command == "":
            continue

        if command in ("q", "quit"):
            return

        if command[0] == "!":
            try:
                coord_str = re.split(' |,', command, 1)[1]
                coord = parse_coord(coord_str)
            except:
                print("invalid input")

            if coord in board["mines"]:
                print("Game Over!")
                board["reveal"] = True
                render_callback(board)
                return
            uncover_tile(board, coord)

        if command[0] == "?":
            try:
                coord_str = re.split(' |,', command, 1)[1]
                coord = {parse_coord(coord_str)}
                board["flags"] ^= coord
            except:
                print("invalid input")

        if command in ("%", "reveal"):
            print(board["mines"])
            board["reveal"] = not board["reveal"]

        if command == "h":
            print("Minesweeper help:")
            print("? (x,y) place flag at specified coordinate")
            print("! (x,y) reveal flag at specified coordinate")
            print("q quit")

def main():
    eventloop(init_gameboard())

if __name__ == "__main__":
    main()
