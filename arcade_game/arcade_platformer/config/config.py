import pathlib

""" This is the main constant for the game """

# Game constants

# Window dimensions
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Hackathon Arcade Game"

# Scaling constants
MAP_SCALING = 1.0

# Player constants
GRAVITY = 1.0
PLAYER_START_X = 65
PLAYER_START_Y = 256
PLAYER_MOVE_SPEED = 6
PLAYER_JUMP_SPEED = 25

# Viewport (horizontal/vertical scroll) margins
# How close do we have to be to scroll the viewport?
# Note the difference between LEFT_VIEWPORT_MARGIN and RIGHT_VIEWPORT_MARGIN.
# This allows the alien to get closer to the left edge than the right.
LEFT_VIEWPORT_MARGIN = 150
RIGHT_VIEWPORT_MARGIN = 300
TOP_VIEWPORT_MARGIN = 150
BOTTOM_VIEWPORT_MARGIN = 150

# Number of lives the player can use to win the game
TOTAL_LIFE_COUNT = 1

# Assets path
ASSETS_PATH = pathlib.Path(__file__).resolve().parent.parent.parent / "assets"
