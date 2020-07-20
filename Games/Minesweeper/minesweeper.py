"""
Minesweeper

Implementation of the game Minesweeper as defined here:
https://rosettacode.org/wiki/Minesweeper_game

by Mark Brown <mark.brown314@gmail.com>
"""
from random import randint, seed
import re
import string
import copy

MAX_X = 10
MAX_Y = 10
MAX_MINES = 10
PERCENT_MINES = .25
RAND_SEED = 1
LABEL = " " + string.ascii_uppercase

class GameContext(object):
    def __init__(self):
        # defaults
        self.rand_seed = RAND_SEED
        self.max_x = MAX_X
        self.max_y = MAX_Y
        self.percent_mines = PERCENT_MINES
        self.max_mines = MAX_MINES
        self.layout_callback = self.default_mine_placement

        self.mines = set()
        self.flags = set()
        self.visible = set()

        # check settings for too many mines
        total_tiles = self.max_x * self.max_y
        check_percent_mines = self.max_mines / total_tiles
        assert check_percent_mines <= self.percent_mines

        self.empty = set()
        self.reveal = False

    def adjecency_check(self, input_set, coord, match=True):
        for x in range(coord[0]-1, coord[0]+2):
            for y in range(coord[1]-1, coord[1]+2):
                if (x, y) == coord:
                    continue
                if match and (x, y) in input_set:
                    yield(x, y)
                if not match and (x, y) not in input_set:
                    yield(x, y)

    def adjecent_mines(self, coord):
        return len([*self.adjecency_check(self.mines, coord)])

    def set_flag(self, coord):
        self.flags ^= coord


    def uncover_tile(self, coord):

        if coord in self.visible:
            return

        # first move init board
        if not self.visible:
            self.layout_callback(coord)      

        if self.adjecent_mines(coord) > 0:
            self.visible.add(coord)
            return

        if coord in self.empty:
            self.visible.add(coord)

        for pos in self.adjecency_check(self.empty, coord):
            self.uncover_tile(pos)

    def render_gameboard(self):
        char = "^"
        for x in range(0, MAX_X + 1):
            print(LABEL[x], end='')
        for y in range(1, MAX_Y + 1):
            print()
            print(LABEL[y], end='')
            for x in range(1, MAX_X + 1):
                if (x, y) in self.flags:
                    char = "?"
                elif (x, y) not in self.visible:
                    char = "#"
                else:
                    mine_count = self.adjecent_mines((x, y))
                    if mine_count == 0:
                        char = "."
                    else:
                        char = str(mine_count)

                if self.reveal and (x, y) in self.mines:
                    char = "*"

                print(char, end="")
        print()

    def winning_condition(self):
        return self.mines and not self.visible ^ self.empty - self.mines
                

    def default_mine_placement(self, initial_coord=None):
        # layout mines: random placement
        seed(self.rand_seed)
        exclude_map = set(self.mines)
        exclude_map.update([*self.adjecency_check(set(), initial_coord, False)])
        exclude_map.update([initial_coord])

        while True:
            if len(self.mines) >= self.max_mines:
                break
            mine_coord = (randint(1, self.max_x), randint(1, self.max_y))
            if mine_coord in exclude_map:
                continue
            self.mines.add(mine_coord)
            exclude_map.add(mine_coord)

        for y in range(1, self.max_y + 1):
            for x in range(1, self.max_x + 1):
                if not (x, y) in self.mines:
                    self.empty.add((x, y))

if __name__ == "__main__":
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

    def eventloop():
        game_context = GameContext()
        undo_list = [copy.deepcopy(game_context)]
        input_callback = input
        game_over = False

        while True:
            # check winning condition
            if game_context.winning_condition():
                print("You Win!!!")
                game_context.reveal = True
                game_context.render_gameboard()
                game_over = True
                return
                    
            game_context.render_gameboard()
            command = input_callback("command (h for help):")
            if command == "":
                continue

            if command in ("q", "quit"):
                return

            if command[0] == "!" and not game_over:
                try:
                    coord_str = re.split(' |,', command, 1)[1]
                    coord = parse_coord(coord_str)
                except:
                    print("invalid input")

                undo_list.append(copy.deepcopy(game_context))
                game_context.uncover_tile(coord)

                if coord in game_context.mines:
                    print("Game Over!")
                    game_context.reveal = True
                    game_over = True
                    continue
    
            if command[0] == "?" and not game_over:
                try:
                    coord_str = re.split(' |,', command, 1)[1]
                    coord = {parse_coord(coord_str)}
                    undo_list.append(copy.deepcopy(game_context))
                    game_context.set_flag(coord)
                except:
                    print("invalid input")

            if command in ("%", "reveal"):
                print(game_context.mines)
                undo_list.append(copy.deepcopy(game_context))
                game_context.reveal = not game_context.reveal

            if command == "h":
                print("Minesweeper help:")
                print("? (x,y) place flag at specified coordinate")
                print("! (x,y) reveal flag at specified coordinate")
                print("q quit")
            
            if command == "restart":
                print("Restarting")
                game_context = GameContext()
                undo_list = [copy.deepcopy(game_context)]

            if command == "undo":
                if undo_list:
                    game_over = False
                    game_context = undo_list.pop()
                else:
                    print("Cannot undo")

    def main():
        eventloop()

    main()
