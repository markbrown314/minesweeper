"""
Minesweeper

Implementation of the game Minesweeper as defined here:
https://rosettacode.org/wiki/Minesweeper_game

by Mark Brown <mark.brown314@gmail.com>
"""
from random import randint, seed
import re
from string import ascii_uppercase
from copy import deepcopy
from math import floor

MAX_X = 10
MAX_Y = 10
MAX_MINES = None
PERCENT_MINES = .10
RAND_SEED = 1
TILE_EMPTY = "."
TILE_MINE = "*"
TILE_FLAG = "?"
TILE_WRONG = "X"
TILE_HIDDEN = "#"


class GameContext():
    """ manages game context """
    def __init__(self, **kwargs):
        # defaults
        self.rand_seed = kwargs.get("rand_seed", RAND_SEED)
        self.max_x = kwargs.get("max_x", MAX_X)
        self.max_y = kwargs.get("max_y", MAX_Y)
        self.percent_mines = kwargs.get("percent_mines", PERCENT_MINES)
        self.max_mines = kwargs.get("max_mines", MAX_MINES)
        self.layout_callback = kwargs.get("layout_callback", self.default_mine_placement)

        self.mines = set()
        self.flags = set()
        self.visible = set()
        self.game_map = {}

        # check settings for too many mines
        total_tiles = self.max_x * self.max_y

        # check mine constraints
        if self.max_mines and self.percent_mines:
            check_percent_mines = self.max_mines / total_tiles
            assert check_percent_mines <= self.percent_mines
        else:
            assert self.percent_mines
            self.max_mines = floor(total_tiles * self.percent_mines)

        self.empty = set()
        self.reveal = False

    @staticmethod
    def adjecency_check(input_set, coord, match=True):
        """ check if coordinate is adjecent to item in input set """
        for x in range(coord[0]-1, coord[0]+2):
            for y in range(coord[1]-1, coord[1]+2):
                if (x, y) == coord:
                    continue
                if match and (x, y) in input_set:
                    yield(x, y)
                if not match and (x, y) not in input_set:
                    yield(x, y)

    def adjecent_mines(self, coord):
        """ check if coordinate is adjecent to mine tile """
        return len([*self.adjecency_check(self.mines, coord)])

    def set_flag(self, coord):
        """ set flag at coordinate """
        self.flags ^= coord


    def uncover_tile(self, coord):
        """ reveal tile at coordinate """
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
        """ construct game map from current game context """
        tile = None
        for y in range(1, self.max_y + 1):
            for x in range(1, self.max_x + 1):
                if (x, y) in self.flags:
                    tile = TILE_FLAG
                elif (x, y) not in self.visible:
                    tile = TILE_HIDDEN
                else:
                    mine_count = self.adjecent_mines((x, y))
                    if mine_count == 0:
                        tile = TILE_EMPTY
                    else:
                        tile = str(mine_count)

                if self.reveal:
                    if (x, y) in self.mines:
                        tile = TILE_MINE
                    elif (x, y) in self.flags and (x, y) not in self.mines:
                        tile = TILE_WRONG

                assert tile
                self.game_map[(x, y)] = tile

    def winning_condition(self):
        """ check for winning condition """
        return self.mines and not self.visible ^ self.empty - self.mines

    def hit_mine(self, coord):
        """ check if coordinate has mine """
        return coord in self.mines

    def default_mine_placement(self, initial_coord=None):
        """ play mines with random location """
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

    def eventloop():
        """ event loop """
        game_context = GameContext()
        undo_list = []
        game_over = False

        while True:
            save_context = deepcopy(game_context)

            if not game_over:
                print_game_context(game_context)

            command = input("command (h for help):")
            if command == "":
                continue

            if command in ("q", "quit"):
                return

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
                    coord = {parse_coord(coord_str)}
                    undo_list.append(save_context)
                    game_context.set_flag(coord)
                except ValueError:
                    print("invalid input")

            if command in ("%", "reveal"):
                print(game_context.mines)
                undo_list.append(save_context)
                game_context.reveal = not game_context.reveal

            if command in ("h", "help"):
                print("Minesweeper help:")
                print("? (x,y) place flag at specified coordinate")
                print("! (x,y) reveal flag at specified coordinate")
                print("q quit")
                print("u undo")
                print("r restart")
                print("h help")

            if command in ("r", "restart"):
                print("Restarting")
                undo_list = []
                game_context = GameContext()

            if command in ("u", "undo"):
                if undo_list:
                    game_over = False
                    game_context = undo_list.pop()
                else:
                    print("Cannot undo")

    def main():
        """ executes if module is not imported """
        eventloop()

    main()
