import simplegui
import random
import json

# Game Parameters.
GAME_TITLE = "Cookie Chase!"
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
LEVEL_TOTAL_SECONDS = 60
# Game Opening Screen parameters
START_BUTTON_WIDTH = 100
START_BUTTON_HEIGHT = 40
START_BUTTON_POS = (SCREEN_WIDTH/2 - START_BUTTON_WIDTH/2, SCREEN_HEIGHT/2)
MENU_PAGE_BACKGROUND = simplegui.load_image("https://img.freepik.com/premium-vector/vector-seamless-pattern-with-cookies-colorful_566075-619.jpg?w=1380")
PLAYER_IMAGE = simplegui.load_image("https://github.com/k1randdd/cookie_sprite/blob/main/cookie_sprite_400_400_transparent_v2.png?raw=true")
COOKIE_IMAGE = simplegui.load_image("https://github.com/k1randdd/cookie_sprite/blob/main/cookie_v2.png?raw=true")


game_palette = {"background_color": "black",
                "sprite_color": "blue",
                "edge_color": "white",
                "grid_color": "grey",
                "checkpoint_color": "brown",
                "danger_color": "red"}

# List of Game Levels.
game_levels = [{
    "name": "Level 1",
    "grid_width": 5,
    "grid_height": 5,
    "start_cell": [0, 0],
    "checkpoints": [""],
    "slabs_h": ["1 1",
                "4 2",
                "2 3",
                "4 4",
                "1 4"],
    "slabs_v": ["3 0",
                "1 2",
                "3 4"],
    }, {
    "name": "Level 2",
    "background_color": "black",
    "sprite_color": "blue",
    "edge_color": "white",
    "grid_color": "grey",
    "checkpoint_color": "brown",
    "danger_color": "red",
    "grid_width": 6,
    "grid_height": 6,
    "start_cell": [2, 2],
    "checkpoints": [""],
    "slabs_h": ["2 1",
                "4 2",
                "2 3",
                "3 3",
                "5 3",
                "0 4",
                "5 5"],
    "slabs_v": ["1 0",
                "5 0",
                "1 2",
                "2 2",
                "3 2",
                "3 3",
                "4 3",
                "2 5",
                "3 5"],
    }
]


# Find the Game Level index 0 to n from the Level Name.
def find_game_level_index(levels: list, level_name: str) -> int:
    found_index = -1
    for i in range(len(levels)):
        if levels[i].get("name", "") == level_name:
            found_index = i
            break
    return found_index


# Class for the GameData.
class GameData:
    # GameData class constructor
    def __init__(self, levels, level_index, canvas):
        # Set the Level Details.
        # NB. must copy any lists (not refer to them),
        #     especially: checkpoints = items are removed from this copy held in GameData.
        self.canvas = canvas
        level = levels[level_index]
        self.name: str = level.get("name", "(No Level Name)")

        # Build default game data. - a small board.
        self.background_color: str = game_palette["background_color"]
        self.sprite_color: str = game_palette["sprite_color"]
        self.edge_color: str = game_palette["edge_color"]
        self.grid_color: str = game_palette["grid_color"]
        self.checkpoint_color: str = game_palette["checkpoint_color"]
        self.danger_color: str = game_palette["danger_color"]
        self.width: int = 2
        self.height: int = 2
        self.start = [0, 0]
        self.checkpoints = ["1 1"]
        self.slabs_h = []
        self.slabs_v = []
        self.checkpoint_slabs_h = []
        self.checkpoint_slabs_v = []
        self.score: int = 0

        # Fill with Level Details.
        self.used_indices = []
        self.build_level_details(game_levels, level_index)
        if self.checkpoints == [""]:  # Fill the board with checkpoints.
            cells_filled = [str(self.start[0]) + " " + str(self.start[1])]
            self.checkpoints = []
            for x in range(self.width):
                for y in range(self.height):
                    position = str(x) + " " + str(y)
                    if position not in cells_filled:
                        self.checkpoints.append(position)

        # Calculations for scaling the game Grid to the Screen size.
        self.max_cells: int = max(self.width, self.height)
        self.cell_pixels: int = int(min(SCREEN_WIDTH, SCREEN_HEIGHT) / self.max_cells)
        self.edge_width: int = max(int(self.cell_pixels / 8), 1)
        self.grid_line_width: int = max(int(self.edge_width / 4), 1)
        self.icon_width: int = max(self.cell_pixels - self.edge_width, 1)
        self.icon_radius: int = int(self.icon_width / 2)
        self.padding: int = int(self.edge_width / 2) + 1

    def build_level_details(self, levels, level_index: int):
        if level_index in self.used_indices:
            return  # Recursive calls cannot apply a level that is already applied.
        level = levels[level_index]
        if level.get("apply_level"):
            i = find_game_level_index(levels, level.get("apply_level"))
            if i >= 0:
                self.used_indices.append(level_index)
                self.build_level_details(levels, i)
        if level.get("background_color"):
            self.background_color = level.get("background_color")
        if level.get("sprite_color"):
            self.sprite_color = level.get("sprite_color")
        if level.get("edge_color"):
            self.edge_color = level.get("edge_color")
        if level.get("grid_color"):
            self.grid_color = level.get("grid_color")
        if level.get("checkpoint_color"):
            self.checkpoint_color = level.get("checkpoint_color")
        if level.get("danger_color"):
            self.danger_color = level.get("danger_color")
        if level.get("grid_width"):
            self.width = level.get("grid_width")
        if level.get("grid_height"):
            self.height = level.get("grid_height")
        if level.get("start_cell"):
            self.start = level.get("start_cell").copy()
        if level.get("checkpoints"):
            self.checkpoints = level.get("checkpoints").copy()
        slabs = level.get("slabs_h")
        if slabs:
            for item in slabs:
                if item in self.slabs_h:
                    self.slabs_h.remove(item)
                else:
                    self.slabs_h.append(item)
        slabs = level.get("slabs_v")
        if slabs:
            for item in slabs:
                if item in self.slabs_v:
                    self.slabs_v.remove(item)
                else:
                    self.slabs_v.append(item)

    # Method to find top left point of grid position
    def get_grid_point_top_left(self, point: list[int]):
        return [point[0] * self.cell_pixels + self.padding,
                point[1] * self.cell_pixels + self.padding]

    # Method to draw the GameData to the screen.
    def draw(self, canvas):
        # Fill the screen: background.
        canvas.draw_polygon([(0, 0), (0, SCREEN_HEIGHT), (SCREEN_WIDTH, SCREEN_HEIGHT), (SCREEN_WIDTH, 0)],
                             1, "", self.background_color)

        # Fill the screen: board grid.
        for x in range(1, self.width):
            canvas.draw_line((x * self.cell_pixels, 0), 
                              (x * self.cell_pixels, self.height * self.cell_pixels - 1), 
                              self.grid_line_width, 
                              self.grid_color)
        for y in range(1, self.height):
            canvas.draw_line((0, y * self.cell_pixels), 
                              (self.width * self.cell_pixels - 1, y * self.cell_pixels), 
                              self.grid_line_width, 
                              self.grid_color)

        # Fill the screen: board edges.
        canvas.draw_polygon([(0, 0), 
                             (0, self.height * self.cell_pixels), 
                             (self.width * self.cell_pixels, self.height * self.cell_pixels), 
                             (self.width * self.cell_pixels, 0)],
                            self.edge_width, 
                            self.edge_color, None)

        # Fill the screen: board - slabs - horizontal.
        for slab in self.slabs_h:  # draw thin Rect, one cell-space to the Right.
            p = slab.split()
            x = int(p[0])
            y = int(p[1])
            canvas.draw_line((x * self.cell_pixels, y * self.cell_pixels), 
                             ((x + 1) * self.cell_pixels, y * self.cell_pixels), 
                             self.edge_width, 
                             self.edge_color)
        # Fill the screen: board - slabs - vertical.
        for slab in self.slabs_v:  # draw thin Rect, one cell-space Downwards.
            p = slab.split()
            x = int(p[0])
            y = int(p[1])
            canvas.draw_line((x * self.cell_pixels, y * self.cell_pixels), 
                             (x * self.cell_pixels, (y + 1) * self.cell_pixels), 
                             self.edge_width, 
                             self.edge_color)

        # Fill the screen: board - checkpoints.
        for checkpoint in self.checkpoints:
            q = checkpoint.split()
            a = [int(q[0]), int(q[1])]
            p = self.get_grid_point_top_left(a)
            p[0] += self.icon_radius
            p[1] += self.icon_radius
            d = max(int(self.icon_radius * 2 / 3), 1)
            """canvas.draw_circle(p, d, 1, self.checkpoint_color, self.checkpoint_color)"""
            canvas.draw_image(COOKIE_IMAGE, (COOKIE_IMAGE.get_width()/2, COOKIE_IMAGE.get_height()/2),
                             (COOKIE_IMAGE.get_width(), COOKIE_IMAGE.get_height()),
                             (p[0], p[1]), (self.icon_width, self.icon_width))

    # Method to check collision between an icon on screen at (x,y) and the Checkpoints list.
    def hit_checkpoint(self, x: int, y: int, excluded_sprite_index: int = -1, check_danger: bool = True):
        # Correct the Screen (x,y) and Grid (px,py) positions, due to Game Board scaling issues.
        px = int(round((x - self.padding) / self.cell_pixels))
        py = int(round((y - self.padding) / self.cell_pixels))
        checkpoint = str(px) + ' ' + str(py)
        if checkpoint in self.checkpoints:
            self.checkpoints.remove(checkpoint)
            self.score += 1
            score_label.set_text("Score: " + str(self.score))

    # Method to return True or False for a completed Game Level.
    def completed_level(self):
        return len(self.checkpoints) == 0

# Create the ball class
class PlayerBall:
    # Ball class constructor
    def __init__(self, x: int, y: int, radius: int, color: str, screen):
        self.x: int = x
        self.y: int = y
        self.radius: int = radius
        self.diameter: int = radius * 2
        self.screen = screen
        self.color: str = color
        # Animation variables.
        self.dx: int = 0
        self.dy: int = 0

    def draw(self, canvas):
        """canvas.draw_circle((self.x + self.radius, self.y + self.radius), 
                           self.radius, 1, self.color, self.color)"""
        canvas.draw_image(PLAYER_IMAGE, (PLAYER_IMAGE.get_width()/2, PLAYER_IMAGE.get_height()/2),
                         (PLAYER_IMAGE.get_width(), PLAYER_IMAGE.get_height()),
                         (self.x + self.radius, self.y + self.radius), (self.diameter, self.diameter))


    # Simple test movement: within the bounds of the entire Grid, and no collision tests.
    def move_simple(self, move_type, game_data):

        if move_type == "UP":
            self.y -= 2
        elif move_type == "DOWN":
            self.y += 2
        elif move_type == "LEFT":
            self.x -= 2
        elif move_type == "RIGHT":
            self.x += 2

        # Ensure that the ball stays within the bounds of the grid.
        if self.x < game_data.padding:
            self.x = game_data.padding
        elif self.x + self.diameter > (game_data.width * game_data.cell_pixels - game_data.padding):
            self.x = (game_data.width * game_data.cell_pixels - game_data.padding) - self.diameter
        if self.y < game_data.padding:
            self.y = game_data.padding
        elif self.y + self.diameter > (game_data.height * game_data.cell_pixels - game_data.padding):
            self.y = (game_data.height * game_data.cell_pixels - game_data.padding) - self.diameter

    def move_shift(self, move_type, game_data):

        # Correct the Screen (x,y) and Grid (px,py) positions, due to Game Board scaling issues.
        px = int(round((self.x - game_data.padding) / game_data.cell_pixels))
        py = int(round((self.y - game_data.padding) / game_data.cell_pixels))
        self.x = px * game_data.cell_pixels + game_data.padding
        self.y = py * game_data.cell_pixels + game_data.padding

        if move_type == "UP":
            if str(px) + ' ' + str(py) not in game_data.slabs_h:
                self.y -= game_data.cell_pixels
        elif move_type == "DOWN":
            if str(px) + ' ' + str(py + 1) not in game_data.slabs_h:
                self.y += game_data.cell_pixels
        elif move_type == "LEFT":
            if str(px) + ' ' + str(py) not in game_data.slabs_v:
                self.x -= game_data.cell_pixels
        elif move_type == "RIGHT":
            if str(px+1) + ' ' + str(py) not in game_data.slabs_v:
                self.x += game_data.cell_pixels

        # Ensure that the ball stays within the bounds of the grid.
        if self.x < game_data.padding:
            self.x = game_data.padding
        elif self.x + self.diameter > (game_data.width * game_data.cell_pixels - game_data.padding):
            self.x = (game_data.width * game_data.cell_pixels - game_data.padding) - self.diameter
        if self.y < game_data.padding:
            self.y = game_data.padding
        elif self.y + self.diameter > (game_data.height * game_data.cell_pixels - game_data.padding):
            self.y = (game_data.height * game_data.cell_pixels - game_data.padding) - self.diameter

    def move_animated(self, game_data):

        # Build list of all player obstacles.
        all_slabs_h = game_data.slabs_h.copy()
        all_slabs_v = game_data.slabs_v.copy()

        qx = (self.x - game_data.padding) / game_data.cell_pixels
        qy = (self.y - game_data.padding) / game_data.cell_pixels
        px = int(round(qx))
        py = int(round(qy))

        if self.dx < 0:
            if px == int(qx + 1):
                position = str(px) + ' ' + str(py)
                if position not in all_slabs_v:
                    self.x += self.dx
                else:
                    self.dx = 0
            else:
                self.x += self.dx
        if self.dx > 0:
            if px == int(qx):
                position = str(px+1) + ' ' + str(py)
                if position not in all_slabs_v:
                    self.x += self.dx
                else:
                    self.dx = 0
            else:
                self.x += self.dx
        if self.dy < 0:
            if py == int(qy + 1):
                position = str(px) + ' ' + str(py)
                if position not in all_slabs_h:
                    self.y += self.dy
                else:
                    self.dy = 0
            else:
                self.y += self.dy
        if self.dy > 0:
            if py == int(qy):
                position = str(px) + ' ' + str(py + 1)
                if position not in all_slabs_h:
                    self.y += self.dy
                else:
                    self.dy = 0
            else:
                self.y += self.dy

        # Ensure that the ball stays within the bounds of the grid.
        if self.x < game_data.padding:
            self.x = game_data.padding
            self.dx = 0
        elif self.x + self.diameter > (game_data.width * game_data.cell_pixels - game_data.padding):
            self.x = (game_data.width * game_data.cell_pixels - game_data.padding) - self.diameter
            self.dx = 0
        if self.y < game_data.padding:
            self.y = game_data.padding
            self.dy = 0
        elif self.y + self.diameter > (game_data.height * game_data.cell_pixels - game_data.padding):
            self.y = (game_data.height * game_data.cell_pixels - game_data.padding) - self.diameter
            self.dy = 0

        if self.dx == 0 and self.dy == 0:
            # Correct the Screen (x,y) and Grid (px,py) positions, due to Game Board scaling issues.
            px = int(round((self.x - game_data.padding) / game_data.cell_pixels))
            py = int(round((self.y - game_data.padding) / game_data.cell_pixels))
            self.x = px * game_data.cell_pixels + game_data.padding
            self.y = py * game_data.cell_pixels + game_data.padding


def draw(canvas):
    global game_running, key_fn, game_board, icon_main, level_index, flag_start_new_level, animated_roll, faster_roll, move_anywhere, timer, ticks_left

    if not game_running:
        # Draw background
        canvas.draw_image(MENU_PAGE_BACKGROUND, (MENU_PAGE_BACKGROUND.get_width()/2, MENU_PAGE_BACKGROUND.get_height()/2),
                         (MENU_PAGE_BACKGROUND.get_width(), MENU_PAGE_BACKGROUND.get_height()),
                         (SCREEN_WIDTH/2, SCREEN_HEIGHT/2), (SCREEN_WIDTH, SCREEN_HEIGHT))
        # Draw title
        canvas.draw_text("Cookie Chase", (SCREEN_WIDTH/2 - 140, SCREEN_HEIGHT/2 - 50), 50, "Black")
        # Draw start button
        canvas.draw_polygon([(START_BUTTON_POS[0], START_BUTTON_POS[1]), 
                             (START_BUTTON_POS[0] + START_BUTTON_WIDTH, START_BUTTON_POS[1]),
                             (START_BUTTON_POS[0] + START_BUTTON_WIDTH, START_BUTTON_POS[1] + START_BUTTON_HEIGHT),
                             (START_BUTTON_POS[0], START_BUTTON_POS[1] + START_BUTTON_HEIGHT)],
                             2, "Black", "Black")                    
        canvas.draw_text("Start", (SCREEN_WIDTH/2 - 25, SCREEN_HEIGHT/2 + 30), 26, "White")
        return

    if flag_start_new_level:
            flag_start_new_level = False
            # Re-Start the timer countdown.
            timer.stop()
            timer_label.set_text("")
            game_board = GameData(game_levels, level_index, canvas)
            game_description = "[" + str(level_index + 1) + " of " + str(len(game_levels)) + "]: " + game_board.name
            level_name_label.set_text(game_description)
            game_board.draw(canvas)
            # Create a new ball object
            start_point = game_board.get_grid_point_top_left(game_board.start)
            icon_main = PlayerBall(start_point[0], start_point[1],
                                   game_board.icon_radius,
                                   game_board.sprite_color, canvas)
            ticks_left = LEVEL_TOTAL_SECONDS
            timer.start()
    game_board.hit_checkpoint(icon_main.x, icon_main.y)
    game_board.draw(canvas)
    icon_main.draw(canvas)
    
    # Move the main icon - three move modes.
    if animated_roll and not move_anywhere:
        if icon_main.dx == 0 and icon_main.dy == 0:
            d = 2
            if faster_roll:
                d = int(game_board.icon_width / 4)
            if key_fn == "UP":  # UP
                icon_main.dy = -d
            if key_fn == "DOWN":  # DOWN
                icon_main.dy = d
            if key_fn == "LEFT":  # LEFT
                icon_main.dx = -d
            if key_fn == "RIGHT":  # RIGHT
                icon_main.dx = d
    elif not move_anywhere:  # Move one cell: useful for gameplay debugging.
        if key_fn in ["UP", "DOWN", "LEFT", "RIGHT"]:
            icon_main.move_shift(key_fn, game_board)
    else:  # Move anywhere on the board, useful for testing.
        if key_fn in ["UP", "DOWN", "LEFT", "RIGHT"]:
            icon_main.move_simple(key_fn, game_board)
    if icon_main.dx != 0 or icon_main.dy != 0:
        icon_main.move_animated(game_board)
    
    if key_fn == "1":  # Reset to default mode.
        animated_roll = True
        faster_roll = False
        move_anywhere = False
    if key_fn == "z":  # Move one cell only.
        animated_roll = False
    if key_fn == "a":  # Roll faster.
        faster_roll = True
    if key_fn == "space": # Move anywhere
        move_anywhere = True
    
    # Restart the current Level, at its original position.
    if key_fn == "0":
        flag_start_new_level = True
    if key_fn == "x":
        flag_start_new_level = True
        timer.stop()
        game_running = False
    # Restart the game, at the Next Level.
    if key_fn == "n":
        level_index += 1
        if level_index >= len(game_levels):
            level_index = 0
        flag_start_new_level = True
    # Restart the game, at the Previous Level.
    if key_fn == "p":
        level_index -= 1
        if level_index < 0:
            level_index = len(game_levels) - 1
        flag_start_new_level = True
    # Restart the game, at a Random Level.
    if key_fn == "r":
        level_index = random.randint(0, len(game_levels) - 1)
        flag_start_new_level = True
    
    if key_fn == "g":
        level_name = input('Enter the level name: ')
        if level_name:
            i = find_game_level_index(game_levels, level_name)
            if i >= 0:
                level_index = i
                flag_start_new_level = True
            else:
                print("Cannot find level name: " + level_name)
    if key_fn == "f":
        filename = input('Enter the filename to save as: ')
        if filename:
            try:
                with open(filename, 'w') as file:
                    file.write(json.dumps(game_levels, indent=4))
            except Exception as e:
                print("Cannot save to file; error: " + str(e))
    if key_fn == "l":
        filename = input('Enter the filename to load: ')
        if filename:
            try:
                with open(filename, 'r') as file:
                    data = json.loads(file.read())
                new_size = len(data)
                while len(game_levels) > new_size:
                    game_levels.pop()
                while len(game_levels) < new_size:
                    game_levels.append(game_levels[0].copy())
                for i in range(new_size):
                    game_levels[i] = data[i].copy()
                data.clear()
            except Exception as e:
                print("Cannot load from file; error: " + str(e))

    # Clear the processed key event, stopping repeat key fns.
    if move_anywhere:
        if key_fn not in ["UP", "DOWN", "LEFT", "RIGHT"]:
            key_fn = ""
    else:
        key_fn = ""

    if game_board is not None:
        # Game Completed: Move on to the next level.
        if game_board.completed_level():
            level_index += 1
            if level_index >= len(game_levels):
                level_index = 0
            flag_start_new_level = True


def keyup(key):
    global key_fn
    key_fn = ""


def keydown(key):
    global game_running, key_fn
    if not game_running:
        return
    key_fn = ""
    if key == simplegui.KEY_MAP["up"]:
        key_fn = "UP"
    if key == simplegui.KEY_MAP["down"]:
        key_fn = "DOWN"
    if key == simplegui.KEY_MAP["left"]:
        key_fn = "LEFT"
    if key == simplegui.KEY_MAP["right"]:
        key_fn = "RIGHT"
    if key == simplegui.KEY_MAP["space"]:
        key_fn = "space"
    for ch in ["h", "g", "a", "z", "f", "l", "1", "0", "p", "n", "r", "x"]:
        if key == simplegui.KEY_MAP[ch]:
            key_fn = ch
            break


def timer_handler():
    global timer, ticks_left, flag_start_new_level
    ticks_left -= 1
    seconds = ticks_left
    timer_label.set_text("Time remaining: " + str(seconds) + " seconds.")
    if ticks_left <= 0:
        flag_start_new_level = True


def mouse_handler(pos):
    global game_running
    if game_running:
        return
    if (pos[0] > START_BUTTON_POS[0] and pos[0] < START_BUTTON_POS[0] + START_BUTTON_WIDTH and 
        pos[1] > START_BUTTON_POS[1] and pos[1] < START_BUTTON_POS[1] + START_BUTTON_HEIGHT):
        game_running = True


def initialize_variables():
    global game_running, key_fn, game_board, icon_main, level_index, flag_start_new_level, animated_roll, faster_roll, move_anywhere, timer, ticks_left
    game_board = None
    icon_main = None
    level_index = 0
    flag_start_new_level = True
    animated_roll = True
    faster_roll = False
    move_anywhere = False
    key_fn = ""
    ticks_left = LEVEL_TOTAL_SECONDS
    timer = simplegui.create_timer(1000, timer_handler)
    game_running = False

    
initialize_variables()            
frame = simplegui.create_frame(GAME_TITLE, SCREEN_WIDTH, SCREEN_HEIGHT)
level_name_label = frame.add_label('Level Name:')
timer_label = frame.add_label('Time remaining: ')
score_label = frame.add_label('Score: ')
frame.add_label('-------------------------')
frame.add_label('Keys:')
frame.add_label(("Use  ' ↑ ↓ → ← '  to move around"))
frame.add_label(": A = Roll faster")
frame.add_label(": Z = Move one cell only")
frame.add_label(": SPACE = Move anywhere")

frame.add_label(": 1 = Set to default rolling mode")
frame.add_label(": 0 = Restart the current level")
frame.add_label(": N = go to the Next level")
frame.add_label(": P = go to the Previous level")
frame.add_label(": R = go to a Random level")
frame.add_label(": G = Go to level <name>")

frame.add_label(": X = Exit game, back to the opening screen.")

frame.set_draw_handler(draw)
frame.set_keydown_handler(keydown)
frame.set_keyup_handler(keyup)
frame.set_mouseclick_handler(mouse_handler)
frame.start()
