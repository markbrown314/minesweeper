"""
Minesweeper

There is an n by m grid that has a random number (between 10% to 20% of the
total number of tiles, though older implementations may use 20%..60% instead)
of randomly placed mines that need to be found.

Positions in the grid are modified by entering their coordinates where the
first coordinate is horizontal in the grid and the second vertical. The top
left of the grid is position 1,1; the bottom right is at n,m.

The total number of mines to be found is shown at the beginning of the game.
Each mine occupies a single grid point, and its position is initially unknown
to the player.

The grid is shown as a rectangle of characters between moves.
You are initially shown all grids as obscured, by a single dot '.'
You may mark what you think is the position of a mine which will show as a '?'
You can mark what you think is free space by entering its coordinates.
If the point is free space then it is cleared, as are any adjacent points that
are also free space. This is repeated recursively for subsequent adjacent free
points unless that point is marked as a mine or is a mine.

Points marked as a mine show as a '?'.
Other free points show as an integer count of the number of adjacent true mines
in its immediate neighborhood, or as a single space ' ' if the free point is
not adjacent to any true mines.

Of course you lose if you try to clear space that has a hidden mine.
You win when you have correctly identified all mines.
The Task is to create a program that allows you to play minesweeper on a 6 by 4
grid, and that assumes all user input is formatted correctly and so checking
inputs for correct form may be omitted. You may also omit all GUI parts of the
task and work using text input and output.

Note: Changes may be made to the method of clearing mines to more closely
follow a particular implementation of the game so long as such differences and
the implementation that they more accurately follow are described.

Implemented with tuple sets
"""
from random import randint, seed
import re

MAX_X = 8
MAX_Y = 8
MAX_MINES = 1
PERCENT_MINES = 25

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

def eventloop():
    board = init_gameboard()
    while True:
        # check winning condition
        if not board["visible"] ^ board["empty"] - board["mines"]:
            print("You Win!!!")
            board["reveal"] = True
            render_gameboard(board)
            return

        render_gameboard(board)
        print("enter in command:")
        command = input()
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
                    render_gameboard(board)
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

def init_gameboard():
    seed(1)
    board = {}
    board["dimensions"] = (MAX_X, MAX_Y)
    board["mines"] = set()
    board["flags"] = set()
    board["visible"] = set()

    assert MAX_MINES / (MAX_X * MAX_Y) < PERCENT_MINES / 100

    board["empty"] = set()
    for y in range(1, MAX_Y + 1):
        for x in range(1, MAX_X + 1):
            if not (x,y) in board["mines"]:
                board["empty"].add((x,y))

    board["reveal"] = False
    
    while True:
        if len(board["mines"]) == MAX_MINES:
            break
        mine_coord = (randint(1, MAX_X), randint(1, MAX_Y))
        if mine_coord in board["mines"]:
            continue
        board["mines"].add(mine_coord)
    print(board["mines"])
    return board

def main():
    eventloop()

main()