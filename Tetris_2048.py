import numpy as np
import stddraw  # the stddraw module is used as a basic graphics library
import random  # used for creating tetrominoes with random types/shapes
from game_grid import GameGrid  # class for modeling the game grid
from tetromino import Tetromino  # class for modeling the tetrominoes
from picture import Picture  # used representing images to display
import os  # used for file and directory operations
from color import Color  # used for coloring the game menu


class Game:
    # MAIN FUNCTION OF THE PROGRAM
    # -------------------------------------------------------------------------------
    # Main function where this program starts execution
    def start(self):
        # set the dimensions of the game grid
        grid_h, grid_w = 20, 12
        # set the size of the drawing canvas
        canvas_h, canvas_w = 40 * grid_h, 40 * grid_w
        stddraw.setCanvasSize(canvas_w, canvas_h)
        # set the scale of the coordinate system
        stddraw.setXscale(-0.5, grid_w - 0.5)
        stddraw.setYscale(-0.5, grid_h - 0.5)

        # create the game grid
        grid = GameGrid(grid_h, grid_w)

        # create the first tetromino to enter the game grid
        # by using the create_tetromino function defined below
        current_tetromino = self.create_tetromino(grid_h, grid_w)
        grid.current_tetromino = current_tetromino
        self.restart = False
        self.is_paused = False
        self.is_finished = False
        self.game_over = False
        # display a simple menu before opening the game
        self.display_game_menu(grid_h, grid_w)
        # main game loop (keyboard interaction for moving the tetromino)
        while True:
            # Checks if the user paused the game
            if stddraw.mousePressed():
                if stddraw.mouseX() <= 10.5 + 0.6 and stddraw.mouseX() >= 10.5 - 0.6:
                    if stddraw.mouseY() <= 18.5 + 0.6 and stddraw.mouseY() >= 10.8 - 0.6:
                        self.is_paused = True
                        print("Stopped")
                        self.display_game_menu(grid_h, grid_w)

            # check user interactions via the keyboard
            if stddraw.hasNextKeyTyped():
                key_typed = stddraw.nextKeyTyped()
                # if the left arrow key has been pressed
                if key_typed == "left":
                    # move the tetromino left by one
                    current_tetromino.move(key_typed, grid)
                # if the right arrow key has been pressed
                elif key_typed == "right":
                    # move the tetromino right by one
                    current_tetromino.move(key_typed, grid)
                # if the down arrow key has been pressed
                elif key_typed == "down":
                    # move the tetromino down by one
                    # (causes the tetromino to fall down faster)
                    current_tetromino.move(key_typed, grid)
                elif key_typed == "up":
                    # rotate the tetromino
                    current_tetromino.rotation(grid, current_tetromino)
                elif key_typed == "p":
                    print("Paused")
                    self.is_paused = not self.is_paused
                    # self.display_game_menu(grid_h, grid_w)

                # clear the queue that stores all the keys pressed/typed
                stddraw.clearKeysTyped()

            if not self.is_paused:
                # move (drop) the tetromino down by 1 at each iteration
                success = current_tetromino.move("down", grid)

            # place the tetromino on the game grid when it cannot go down anymore
            if not success:
                # get the tile matrix of the tetromino
                tiles_to_place = current_tetromino.tile_matrix
                # update the game grid by adding the tiles of the tetromino
                self.game_over = grid.update_grid(tiles_to_place)
                # end the main game loop if the game is over

                merge = self.check_merging(grid)
                while merge:
                    merge = self.check_merging(grid)

                row_count = self.is_full(grid_h, grid_w, grid)
                index = 0

                while index < grid_h:
                    while row_count[index]:
                        self.slide_down(row_count, grid)
                        row_count = self.is_full(grid_h, grid_w, grid)
                    index += 1

                labels, num_labels = self.connected_component_labeling(grid.tile_matrix, grid_w, grid_h)
                free_tiles = [[False for v in range(grid_w)] for b in range(grid_h)]
                free_tiles, num_free = self.find_free_tiles(grid_h, grid_w, labels, free_tiles)
                grid.move_free_tiles(free_tiles)


                while num_free != 0:
                    labels, num_labels = self.connected_component_labeling(grid.tile_matrix, grid_w, grid_h)
                    free_tiles = [[False for v in range(grid_w)] for b in range(grid_h)]
                    free_tiles, num_free = self.find_free_tiles(grid_h, grid_w, labels, free_tiles)
                    grid.move_free_tiles(free_tiles)

                labels, num_labels = self.connected_component_labeling(grid.tile_matrix, grid_w, grid_h)
                merge = self.check_merging(grid)
                while merge:
                    merge = self.check_merging(grid)

                row_count = self.is_full(grid_h, grid_w, grid)
                index = 0

                while index < grid_h:
                    while row_count[index]:
                        self.slide_down(row_count, grid)
                        row_count = self.is_full(grid_h, grid_w, grid)
                    index += 1

                """
                while num_free != 0:
                    labels, num_labels = self.connected_component_labeling(grid.tile_matrix, grid_w, grid_h)
                    free_tiles, num_free = self.find_free_tiles(grid_h, grid_w, labels, free_tiles)
                    grid.move_free_tiles(free_tiles)
                """
                # print(labels)
                # print(num_labels)

                if self.game_over:
                    print("Game Over")
                    self.is_finished = True
                    self.display_game_menu(grid_h, grid_w)

                # create the next tetromino to enter the game grid
                # by using the create_tetromino function defined below
                current_tetromino = self.create_tetromino(grid_h, grid_w)
                grid.current_tetromino = current_tetromino

            if self.restart:
                print("Restart")
                for a in range(0, 20):
                    for b in range(12):
                        grid.tile_matrix[a][b] = None
                self.restart = False
                grid.game_over = False

                current_tetromino = self.create_tetromino(grid_h, grid_w)
                grid.current_tetromino = current_tetromino

            # display the game grid and as well the current tetromino
            grid.display()

        # print("Game over")

    def check_merging(self, grid):
        merged = False
        for a in range(0, 19):
            for b in range(12):
                if grid.tile_matrix[a][b] != None and grid.tile_matrix[a + 1][b] != None:
                    if grid.tile_matrix[a][b].number == grid.tile_matrix[a + 1][b].number:
                        grid.tile_matrix[a + 1][b].set_position(None)
                        grid.tile_matrix[a + 1][b] = None
                        grid.tile_matrix[a][b].number += grid.tile_matrix[a][b].number
                        grid.tile_matrix[a][b].updateColor(grid.tile_matrix[a][b].number)
                        merged = True
        return merged

    def is_full(self, grid_h, grid_w, grid):
        row_count = [False for i in range(grid_h)]
        for h in range(grid_h):
            counter = 0
            for w in range(grid_w):
                if grid.is_occupied(h, w):
                    counter += 1
                if counter == 12:
                    row_count[h] = True
        return row_count

    def slide_down(self, row_count, grid):
        for index, i in enumerate(row_count):
            if i:
                for a in range(index, 19):
                    row = np.copy(grid.tile_matrix[a + 1])
                    grid.tile_matrix[a] = row
                    for b in range(12):
                        if grid.tile_matrix[a][b] is not None:
                            grid.tile_matrix[a][b].move(0, -1)
                break

    # Function for creating random shaped tetrominoes to enter the game grid
    def create_tetromino(self, grid_height, grid_width):
        self.rotated = False
        # type (shape) of the tetromino is determined randomly
        tetromino_types = ['I', 'O', 'Z', 'J', 'L', 'T', 'S']
        random_index = random.randint(0, len(tetromino_types) - 1)
        self.random_type = tetromino_types[random_index]
        # create and return the tetromino
        tetromino = Tetromino(self.random_type, grid_height, grid_width)
        return tetromino

    # Function for displaying a simple menu before starting the game
    def display_game_menu(self, grid_height, grid_width):
        # colors used for the menu
        background_color = Color(42, 69, 99)
        button_color = Color(25, 255, 228)
        text_color = Color(31, 160, 239)
        # clear the background canvas to background_color
        stddraw.clear(background_color)
        # get the directory in which this python code file is placed
        current_dir = os.path.dirname(os.path.realpath(__file__))
        # path of the image file
        img_file = current_dir + "/menu_image.png"
        # center coordinates to display the image
        img_center_x, img_center_y = (grid_width - 1) / 2, grid_height - 7
        # image is represented using the Picture class
        image_to_display = Picture(img_file)
        # display the image
        stddraw.picture(image_to_display, img_center_x, img_center_y)
        # dimensions of the start game button
        button_w, button_h = grid_width - 1.5, 2
        # coordinates of the bottom left corner of the start game button
        button_blc_x, button_blc_y = img_center_x - button_w / 2, 4
        # display the start game button as a filled rectangle
        stddraw.setPenColor(button_color)
        stddraw.filledRectangle(button_blc_x, button_blc_y, button_w, button_h)
        # display the text on the start game button
        stddraw.setFontFamily("Arial")
        stddraw.setFontSize(25)
        stddraw.setPenColor(text_color)

        if not self.is_finished and self.is_paused:
            stddraw.setPenColor(button_color)
            button2_blc_x, button2_blc_y = img_center_x - button_w / 2, 1
            stddraw.filledRectangle(button_blc_x, button_blc_y - 3, button_w, button_h)
            stddraw.setFontFamily("Arial")
            stddraw.setFontSize(25)
            stddraw.setPenColor(text_color)

            text_to_display = "Continue"
            stddraw.text(img_center_x, 5, text_to_display)

            text1_to_display = "Restart"
            stddraw.text(img_center_x, 2, text1_to_display)
            while True:
                stddraw.show(50)
                if stddraw.mousePressed():
                    # get the x and y coordinates of the location at which the mouse has
                    # most recently been left-clicked
                    mouse_x, mouse_y = stddraw.mouseX(), stddraw.mouseY()
                    if mouse_x >= button_blc_x and mouse_x <= button_blc_x + button_w:
                        if mouse_y >= button_blc_y and mouse_y <= button_blc_y + button_h:
                            self.is_paused = False
                            break
                        elif mouse_y >= button2_blc_y and mouse_y <= button2_blc_y + button_h:
                            self.restart = True
                            self.is_paused = False
                            break

        elif self.is_finished:
            stddraw.setPenColor(Color(232, 38, 38))
            stddraw.text(img_center_x, 8, "Game Over")
            stddraw.setPenColor(text_color)
            text1_to_display = "Restart"
            stddraw.text(img_center_x, 5, text1_to_display)
            while True:
                stddraw.show(50)
                if stddraw.mousePressed():
                    # get the x and y coordinates of the location at which the mouse has
                    # most recently been left-clicked
                    mouse_x, mouse_y = stddraw.mouseX(), stddraw.mouseY()
                    if mouse_x >= button_blc_x and mouse_x <= button_blc_x + button_w:
                        if mouse_y >= button_blc_y and mouse_y <= button_blc_y + button_h:
                            self.restart = True
                            self.is_paused = False
                            self.is_finished = False
                            self.game_over = False
                            print(self.game_over, self.is_finished)
                            break

        else:
            text1_to_display = "Start Game"
            stddraw.text(img_center_x, 5, text1_to_display)
            # menu interaction loop
            while True:
                # display the menu and wait for a short time (50 ms)
                stddraw.show(50)
                # check if the mouse has been left-clicked
                if stddraw.mousePressed():
                    # get the x and y coordinates of the location at which the mouse has
                    # most recently been left-clicked
                    mouse_x, mouse_y = stddraw.mouseX(), stddraw.mouseY()
                    if mouse_x >= button_blc_x and mouse_x <= button_blc_x + button_w:
                        if mouse_y >= button_blc_y and mouse_y <= button_blc_y + button_h:
                            break  # break the loop to end the method and start the game

    def connected_component_labeling(self, grid, grid_w, grid_h):
        # initially all the pixels in the image are labeled as 0 (background)
        labels = np.zeros([grid_h, grid_w], dtype=int)
        # min_equivalent_labels list is used to store min equivalent label for each label
        min_equivalent_labels = []
        # labeling starts with 1 (as 0 is considered as the background of the image)
        current_label = 1
        # first pass to assign initial labels and determine minimum equivalent labels
        # from conflicts for each pixel in the given binary image
        # --------------------------------------------------------------------------------
        for y in range(grid_h):
            for x in range(grid_w):
                if grid[y, x] is None:
                    continue
                # get the set of neighboring labels for this pixel
                # using get_neighbor_labels function defined below
                neighbor_labels = self.get_neighbor_labels(labels, (x, y))
                # if all the neighbor pixels are background pixels
                if len(neighbor_labels) == 0:
                    # assign current_label as the label of this pixel
                    # and increase current_label by 1
                    labels[y, x] = current_label
                    current_label += 1
                    # initially the minimum equivalent label is the label itself
                    min_equivalent_labels.append(labels[y, x])
                # if there is at least one non-background neighbor
                else:
                    # assign minimum neighbor label as the label of this pixel
                    labels[y, x] = min(neighbor_labels)
                    # a conflict occurs if there are multiple (different) neighbor labels
                    if len(neighbor_labels) > 1:
                        labels_to_merge = set()
                        # add min equivalent label for each neighbor to labels_to_merge set
                        for l in neighbor_labels:
                            labels_to_merge.add(min_equivalent_labels[l - 1])
                        # update minimum equivalent labels related to this conflict
                        # using update_equivalent_labels function defined below
                        self.update_min_equivalent_labels(min_equivalent_labels, labels_to_merge)
        # second pass to rearrange equivalent labels so they all have consecutive values
        # starting from 1 and assign min equivalent label of each pixel as its own label
        # --------------------------------------------------------------------------------
        # rearrange min equivalent labels using rearrange_min_equivalent_labels function
        self.rearrange_min_equivalent_labels(min_equivalent_labels)
        # for each pixel in the given binary image
        for y in range(grid_h):
            for x in range(grid_w):
                # get the value of the pixel
                if grid[y, x] is None:
                    continue
                # assign minimum equivalent label of each pixel as its own label
                labels[y, x] = min_equivalent_labels[labels[y, x] - 1]
        # return the labels matrix and the number of different labels
        return labels, len(set(min_equivalent_labels))

    # Function for getting labels of the neighbors of a given pixel
    def get_neighbor_labels(self, label_values, pixel_indices):
        x, y = pixel_indices
        # using a set to store different neighbor labels without any duplicates
        neighbor_labels = set()
        # add upper pixel to the set if the current pixel is not in the first row of the
        # image and its value is not zero (not a background pixel)
        if y != 0:
            u = label_values[y - 1, x]
            if u != 0:
                neighbor_labels.add(u)
        # add left pixel to the set if the current pixel is not in the first column of
        # the image and its value is not zero (not a background pixel)
        if x != 0:
            l = label_values[y, x - 1]
            if l != 0:
                neighbor_labels.add(l)
        # return the set of neighbor labels
        return neighbor_labels

    # Function for updating min equivalent labels by merging conflicting neighbor labels
    # as the smallest value among their min equivalent labels
    def update_min_equivalent_labels(self, all_min_eq_labels, min_eq_labels_to_merge):
        # find the min value among conflicting neighbor labels
        min_value = min(min_eq_labels_to_merge)
        # for each minimum equivalent label
        for index in range(len(all_min_eq_labels)):
            # if its value is in min_eq_labels_to_merge
            if all_min_eq_labels[index] in min_eq_labels_to_merge:
                # update its value as the min_value
                all_min_eq_labels[index] = min_value

    # Function for rearranging min equivalent labels so they all have consecutive values
    # starting from 1
    def rearrange_min_equivalent_labels(self, min_equivalent_labels):
        # find different values of min equivalent labels and sort them in increasing order
        different_labels = set(min_equivalent_labels)
        different_labels_sorted = sorted(different_labels)
        # create an array for storing new (consecutive) values for min equivalent labels
        new_labels = np.zeros(max(min_equivalent_labels) + 1, dtype=int)
        count = 1  # first label value to assign
        # for each different label value (sorted in increasing order)
        for l in different_labels_sorted:
            # determine the new label
            new_labels[l] = count
            count += 1  # increase count by 1 so that new label values are consecutive
        # assign new values of each minimum equivalent label
        for ind in range(len(min_equivalent_labels)):
            old_label = min_equivalent_labels[ind]
            new_label = new_labels[old_label]
            min_equivalent_labels[ind] = new_label

    def find_free_tiles(self, grid_h, grid_w, labels, free_tiles):
        counter = 0
        okay_labels = []
        for x in range(grid_h):
            for y in range(grid_w):
                if labels[x, y] != 1 and labels[x, y] != 0:
                    if x == 0:
                        okay_labels.append(labels[x, y])
                    if not okay_labels.count(labels[x, y]):
                        free_tiles[x][y] = True
                        counter += 1
        return free_tiles, counter

# start() function is specified as the entry point (main function) from which
# the program starts execution
game = Game()
game.start()
