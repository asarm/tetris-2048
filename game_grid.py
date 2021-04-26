import stddraw  # the stddraw module is used as a basic graphics library
from color import Color  # used for coloring the game grid
import numpy as np  # fundamental Python module for scientific computing
import copy
from point import Point

# Class used for modelling the game grid
from tile import Tile


class GameGrid:
    # Constructor for creating the game grid based on the given arguments
    def __init__(self, grid_h, grid_w):
        # set the dimensions of the game grid as the given arguments
        self.grid_height = grid_h
        self.grid_width = grid_w
        # create the tile matrix to store the tiles placed on the game grid
        self.tile_matrix = np.full((grid_h, grid_w), None)
        # the tetromino that is currently being moved on the game grid
        self.current_tetromino = None
        # game_over flag shows whether the game is over/completed or not
        self.game_over = False
        # set the color used for the empty grid cells
        self.empty_cell_color = Color(15, 15, 15)
        # set the colors used for the grid lines and the grid boundaries
        self.line_color = Color(54, 54, 54)
        self.boundary_color = Color(28, 15, 69)
        # thickness values used for the grid lines and the grid boundaries
        self.line_thickness = 0.002
        self.box_thickness = 8 * self.line_thickness
        self.score = 0
        self.next_tetromino = None
        self.pos = Point()
        self.game_speed = 200
    # Method used for displaying the game grid
    def display(self):
        # clear the background canvas to empty_cell_color
        stddraw.clear(self.empty_cell_color)
        # draw the game grid
        self.draw_grid()
        # draw the current (active) tetromino
        if self.current_tetromino != None and self.next_tetromino != None:
            self.current_tetromino.draw()
            self.next_tetromino.draw()

        # draw a box around the game grid
        self.draw_boundaries()
        # show the resulting drawing with a pause duration = game_speed ms
        stddraw.show(self.game_speed)

    # Method for drawing the cells and the lines of the grid
    def draw_grid(self):
        # draw each cell of the game grid
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                # draw the tile if the grid cell is occupied by a tile
                if self.tile_matrix[row][col] != None:
                    self.tile_matrix[row][col].draw()


        # stop button
        stddraw.setPenColor(Color(230, 79, 79))
        stddraw.filledRectangle(10.5, 18.5, .6, .6)
        stddraw.setPenRadius(100)
        stddraw.setPenColor(Color(255, 255, 255))
        text_to_display = "| |"
        stddraw.text(10.8, 18.8, text_to_display)

        self.drawScore(self.score)

        # draw the inner lines of the grid
        stddraw.setPenColor(self.line_color)
        stddraw.setPenRadius(self.line_thickness)
        # x and y ranges for the game grid
        #start_x, end_x = -0.5, self.grid_width - 0.5
        start_x, end_x = -0.5, 12 - 0.5
        start_y, end_y = -0.5, self.grid_height - 0.5
        for x in np.arange(start_x + 1, end_x, 1):  # vertical inner lines
            stddraw.line(x, start_y, x, end_y)
        for y in np.arange(start_y + 1, end_y, 1):  # horizontal inner lines
            stddraw.line(start_x, y, end_x, y)
        stddraw.setPenRadius()  # reset the pen radius to its default value

    # Method for drawing the boundaries around the game grid
    def draw_boundaries(self):
        # draw a bounding box around the game grid as a rectangle
        stddraw.setPenColor(self.boundary_color)  # using boundary_color
        # set the pen radius as box_thickness (half of this thickness is visible
        # for the bounding box as its lines lie on the boundaries of the canvas)
        stddraw.setPenRadius(self.box_thickness)
        # coordinates of the bottom left corner of the game grid
        pos_x, pos_y = -0.5, -0.5
        stddraw.rectangle(pos_x, pos_y, self.grid_width, self.grid_height)
        stddraw.setPenRadius()  # reset the pen radius to its default value

    # Method used for checking whether the grid cell with given row and column
    # indexes is occupied by a tile or empty
    def is_occupied(self, row, col):
        # return False if the cell is out of the grid
        if not self.is_inside(row, col):
            return False
        # the cell is occupied by a tile if it is not None
        return self.tile_matrix[row][col] != None

    # Method used for checking whether the cell with given row and column indexes
    # is inside the game grid or not
    def is_inside(self, row, col):
        if row < 0 or row >= self.grid_height:
            return False
        if col < 0 or col >= self.grid_width:
            return False
        return True

    # Method for updating the game grid by placing the given tiles of a stopped
    # tetromino and checking if the game is over due to having tiles above the
    # topmost game grid row. The method returns True when the game is over and
    # False otherwise.
    def update_grid(self, tiles_to_place):
        # place all the tiles of the stopped tetromino onto the game grid
        n_rows, n_cols = len(tiles_to_place), len(tiles_to_place[0])
        for col in range(n_cols):
            for row in range(n_rows):
                # place each occupied tile onto the game grid
                if tiles_to_place[row][col] != None:
                    pos = tiles_to_place[row][col].get_position()
                    if self.is_inside(pos.y, pos.x):
                        self.tile_matrix[pos.y][pos.x] = tiles_to_place[row][col]
                    # the game is over if any placed tile is out of the game grid
                    else:
                        self.game_over = True
        # return the game_over flag
        return self.game_over

    def move_free_tiles(self, free_tiles):
        for row in range(self.grid_height):  # excluding the bottommost row
            for col in range(self.grid_width):
                if free_tiles[row][col]:
                    free_tile_copy = copy.deepcopy(self.tile_matrix[row][col])
                    self.tile_matrix[row - 1][col] = free_tile_copy
                    dx, dy = 0, -1  # change of the position in x and y directions
                    self.tile_matrix[row - 1][col].move(dx, dy)
                    self.tile_matrix[row][col] = None

    def drawScore(self, score=0):
        stddraw.setPenRadius(150)
        stddraw.setPenColor(Color(255, 255, 255))
        text_to_display = "Score: "+str(score)
        stddraw.text(15.8, 18.8, text_to_display)

    def set_next(self, next_tetromino):
        self.next_tetromino = next_tetromino

    def draw_next(self):
        print(self.next_tetromino.type)
        n = len(self.next_tetromino.occupied_tiles)
        pos = Point()
        pos.x = 13
        pos.y = 13
        for i in range(10, 15):
            for j in range(10, 15):
                self.tile_matrix[i][j] = None
        self.next_tetromino.move_pos(13,13)
        # self.next_tetromino.tile_matrix[0][1].set_position(pos)