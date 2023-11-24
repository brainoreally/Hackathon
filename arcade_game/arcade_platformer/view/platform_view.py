import logging
from time import sleep
from timeit import default_timer
import arcade

from arcade_game.arcade_platformer.config.config import SCREEN_WIDTH, SCREEN_HEIGHT, TOTAL_LIFE_COUNT, ASSETS_PATH, \
    MAP_SCALING, PLAYER_START_X, PLAYER_START_Y, GRAVITY, LEFT_VIEWPORT_MARGIN, RIGHT_VIEWPORT_MARGIN, \
    TOP_VIEWPORT_MARGIN, BOTTOM_VIEWPORT_MARGIN
from arcade_game.arcade_platformer.player.player import Player
from arcade_game.arcade_platformer.enemy.enemy import Enemy
from . import game_over_view, winner_view
from arcade_game.arcade_platformer.helpers.speech_recognition import SpeechRecognition


class PlatformerView(arcade.View):
    """
    Displays the platform game view, where you can interact with the player
    """
    def __init__(self, player: Player, speech_recognition: SpeechRecognition) -> None:
        """The init method runs only once when the game starts"""
        super().__init__()

        self.player = player

        self.speech_recognition = speech_recognition
        # logging.info(self.speech_recognition)

        # These lists will hold different sets of sprites
        self.coins = None
        self.background = None
        self.walls = None
        self.ladders = None
        self.goals = None
        self.traps = None

        self.font_size = 16
        # Avoids leaving the mouse pointer in the middle
        self.window.set_mouse_visible(False)

        # One sprite for the player, no more is needed
        self.player_sprite = self.player.sprite

        # We need a physics engine as well
        self.physics_engine = None

        # Someplace to keep score for level and game
        self.level_score = 0

        # Life count init
        self.life_count = TOTAL_LIFE_COUNT

        # Start the timer
        self.time_start = default_timer()  # integer, expressing the time in seconds

        # Which level are we on?
        self.level = 1

        # Instantiate some variables that we will initialise in the setup function
        self.map_width = 0
        self.view_left = 0
        self.view_bottom = 0

        # Load up our sound effects here
        self.ready_sound = arcade.load_sound(
            str(ASSETS_PATH / "sounds" / "ready.wav")
        )
        self.go_sound = arcade.load_sound(
            str(ASSETS_PATH / "sounds" / "go.wav")
        )
        self.coin_sound = arcade.load_sound(
            str(ASSETS_PATH / "sounds" / "coin.wav")
        )
        self.jump_sound = arcade.load_sound(
            str(ASSETS_PATH / "sounds" / "jump.wav")
        )
        self.level_victory_sound = arcade.load_sound(
            str(ASSETS_PATH / "sounds" / "level_victory.wav")
        )
        self.death_sound = arcade.load_sound(
            str(ASSETS_PATH / "sounds" / "death.wav")
        )
        self.background_music = arcade.load_sound(
            str(ASSETS_PATH / "sounds" / "background.wav")
        )
        self.background_music_player = arcade.play_sound(self.background_music, 0.3, 0, True)


        # Play the game start sound animation
        # There is a lag with the 1st sound played so to avoid having a lag during the game
        # when we take the 1st coin we play a sound for the start of the game
        arcade.play_sound(self.ready_sound)
        sleep(1)
        arcade.play_sound(self.go_sound)
        self.setup()

    def setup(self):
        """Sets up the game for the current level. This runs every time we load a new level"""

        # Reset the level score
        self.level_score = 0

        # Get the current map based on the level
        map_name = f"platform_level_{self.level:02}.tmx"
        map_path = ASSETS_PATH / map_name

        # use_spatial_hash : If set to True, this will make moving a sprite in the SpriteList slower,
        # but it will speed up collision detection with items in the SpriteList.
        # Great for doing collision detection with static walls/platforms.
        layer_options = {
            "background": {"use_spatial_hash": False},
            "coins": {"use_spatial_hash": True},
        }

        # Load the current map
        game_map = arcade.load_tilemap(
            map_path, layer_options=layer_options, scaling=MAP_SCALING
        )

        # Load the layers
        self.background = game_map.sprite_lists["background"]
        self.goals = game_map.sprite_lists["goal"]
        self.walls = game_map.sprite_lists["ground"]
        self.coins = game_map.sprite_lists["coins"]

        # Only load ladders in maps with some ladders
        if "ladders" in game_map.sprite_lists:
            self.ladders = game_map.sprite_lists["ladders"]

        # Only load traps in maps with some traps
        if "traps" in game_map.sprite_lists:
            self.traps = game_map.sprite_lists["traps"]

        # Set the background color
        background_color = arcade.color.FRESH_AIR
        if game_map.background_color:
            background_color = game_map.background_color
        arcade.set_background_color(background_color)

        # Find the edge of the map to control viewport scrolling
        # game_map.width : width expressed in number of tiles
        # game_map.tile_width : width of a given tile in pixels
        # Subtracting 1 from game_map.width corrects for the tile indexing used by Tiled.
        self.map_width = (game_map.width - 1) * game_map.tile_width

        # Create the player sprite if they're not already set up
        if not self.player_sprite:
            self.player_sprite = Player().create_player_sprite()

        # Move the player sprite back to the beginning
        self.player_sprite.center_x = PLAYER_START_X
        self.player_sprite.center_y = PLAYER_START_Y
        self.player_sprite.change_x = 0
        self.player_sprite.change_y = 0

        # Set up our enemies
        self.enemies = self.create_enemy_sprites()

        # Reset the viewport (horizontal scroll)
        self.view_left = 0
        self.view_bottom = 0

        # Load the physics engine for this map
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            player_sprite=self.player_sprite,
            platforms=self.walls,
            gravity_constant=GRAVITY,
            ladders=self.ladders,
        )
        self.player.set_physics_engine(self.physics_engine)

    def get_game_time(self) -> int:
        """Returns the number of seconds since the game was initialised"""
        return int(default_timer() - self.time_start)

    def scroll_viewport(self) -> None:
        """
        Scrolls the viewport, horizontally and vertically, when the player gets close to the edges
        This also catches the player falling from a platform, which counts as a death
        """
        # Scroll left
        # Find the current left boundary
        left_boundary = self.view_left + LEFT_VIEWPORT_MARGIN

        # Are we to the left of this boundary? Then we should scroll left.
        if self.player_sprite.left < left_boundary:
            self.view_left -= left_boundary - self.player_sprite.left
            # But don't scroll past the left edge of the map
            if self.view_left < 0:
                self.view_left = 0

        # Scroll right
        # Find the current right boundary
        right_boundary = self.view_left + SCREEN_WIDTH - RIGHT_VIEWPORT_MARGIN

        # Are we to the right of this boundary? Then we should scroll right.
        if self.player_sprite.right > right_boundary:
            self.view_left += self.player_sprite.right - right_boundary
            # Don't scroll past the right edge of the map
            if self.view_left > self.map_width - SCREEN_WIDTH:
                self.view_left = self.map_width - SCREEN_WIDTH

        # Scroll up
        top_boundary = self.view_bottom + SCREEN_HEIGHT - TOP_VIEWPORT_MARGIN
        if self.player_sprite.top > top_boundary:
            self.view_bottom += self.player_sprite.top - top_boundary

        # Scroll down
        bottom_boundary = self.view_bottom + BOTTOM_VIEWPORT_MARGIN
        if self.player_sprite.bottom < bottom_boundary:
            self.view_bottom -= bottom_boundary - self.player_sprite.bottom

        # Catch a fall of the platform
        # -300 rather than 0 is to let the player fall a bit longer, it looks better
        if self.player_sprite.bottom < -300:
            self.handle_player_death()
            return

        # Only scroll to integers, otherwise we end up with pixels that don't line up on the screen.
        self.view_bottom = int(self.view_bottom)
        self.view_left = int(self.view_left)

        # Do the actual scrolling
        arcade.set_viewport(
            left=self.view_left,
            right=SCREEN_WIDTH + self.view_left,
            bottom=self.view_bottom,
            top=SCREEN_HEIGHT + self.view_bottom,
        )

    def handle_player_death(self):
        """
            The player has fallen off the platform or walked into a trap:
            - Play a death sound
            - Decrease life counter
            - Send it back to the beginning of the level
            - Face the player forward
        """

        # Play the death sound
        arcade.play_sound(self.death_sound)
        # Add 1 second of waiting time to let the user understand they fell
        sleep(1)
        # Decrease life count
        self.life_count -= 1
        # Check if the player has any life left, if not trigger the game over animation
        if self.life_count == 0:
            self.handle_game_over()
        else:
            # Back to the level's beginning
            self.setup()
            # Set the player to face right, otherwise it looks odd as the player still looks like falling
            self.player_sprite.state = arcade.FACE_RIGHT

    def on_key_press(self, key: int, modifiers: int):
        """Processes key presses

        Arguments:
            key {int} -- Which key was pressed
            modifiers {int} -- Which modifiers were down at the time
        """

        # Check for player left or right movement
        if key in [arcade.key.LEFT, arcade.key.A]:  # Either left key or A key to go left
            self.player.move_left()

        elif key in [arcade.key.RIGHT, arcade.key.D]:  # Either right key or D key to go right
            self.player.move_right()

        # Check if player can climb up or down
        elif key in [arcade.key.UP, arcade.key.W]:  # Either up key or W key to go up
            self.player.move_up()

        elif key in [arcade.key.DOWN, arcade.key.D]:  # Either down key or D key to down
            self.player.move_down()

        # Check if player can jump
        elif key == arcade.key.SPACE:
            self.player.jump()

    def on_key_release(self, key: int, modifiers: int):
        """Processes key releases

        Arguments:
            key {int} -- Which key was released
            modifiers {int} -- Which modifiers were down at the time
        """
        # Check for player left or right movement
        if key in [
            arcade.key.LEFT,
            arcade.key.A,
            arcade.key.RIGHT,
            arcade.key.D,
        ]:
            self.player.reset_change_x()

        # Check if player can climb up or down
        elif key in [
            arcade.key.UP,
            arcade.key.W,
            arcade.key.DOWN,
            arcade.key.S,
        ]:
            if self.physics_engine.is_on_ladder():
                self.player.reset_change_y()
    
    def on_update(self, delta_time: float):
        """Updates the position of all game objects

        Arguments:
            delta_time {float} -- How much time since the last call
        """
        self.handle_voice_command()

        # Update the player animation
        self.player_sprite.update_animation(delta_time)

        # Update player movement based on the physics engine
        self.physics_engine.update()

        # Restrict user movement so they can't walk off-screen
        if self.player_sprite.left < 0:
            self.player_sprite.left = 0

        # Check if we've picked up a coin
        coins_hit = arcade.check_for_collision_with_list(
            sprite=self.player_sprite, sprite_list=self.coins
        )

        for coin in coins_hit:
            # Add the coin score to our score
            self.level_score += int(coin.properties["point_value"])

            # Play the coin sound
            arcade.play_sound(self.coin_sound)

            # Remove the coin
            coin.remove_from_sprite_lists()

        # Check for trap collision, only in maps with traps
        if self.traps is not None:
            trap_hit = arcade.check_for_collision_with_list(
                sprite=self.player_sprite, sprite_list=self.traps
            )

            if trap_hit:
                self.handle_player_death()
                return

        if self.enemies is not None:
            enemies_hit = arcade.check_for_collision_with_list(
                sprite=self.player_sprite, sprite_list=self.enemies
            )

            if enemies_hit:
                self.handle_player_death()
                return

        # Now check if we are at the ending goal
        goals_hit = arcade.check_for_collision_with_list(
            sprite=self.player_sprite, sprite_list=self.goals
        )

        if goals_hit:
            self.calculate_score()
            if self.level == 5:  # Game is finished : Victory !
                self.handle_victory()
            else:
                # Play the level victory sound
                self.level_victory_sound.play()
                # Add a small waiting time to avoid jumping too quickly into the next level
                sleep(1)

                # Set up the next level and call setup again to load the new map
                self.level += 1
                self.setup()
        else:
            # Set the viewport, scrolling if necessary
            self.scroll_viewport()

        # Are there enemies? Update them as well
        self.enemies.update_animation(delta_time)
        for enemy in self.enemies:
            enemy.center_x += enemy.change_x
            walls_hit = arcade.check_for_collision_with_list(
                sprite=enemy, sprite_list=self.walls
            )
            if walls_hit:
                enemy.change_x *= -1

    def handle_game_over(self):
        """
        Game Over !
        """
        arcade.stop_sound(self.background_music_player)

        # Show the Game Over Screen
        self.calculate_score()
        _game_over_view = game_over_view.GameOverView(self.player, self.speech_recognition)
        self.window.show_view(_game_over_view)

    def handle_victory(self):
        """
        Victory !
        """
        arcade.stop_sound(self.background_music_player)

        # Show the winner Screen
        _winner_view = winner_view.WinnerView(self.player, self.speech_recognition)
        # Calculate final score
        self.window.show_view(_winner_view)

    def calculate_score(self) -> int:
        """
        The final score is the score (gained by collecting coins)
        plus a time bonus
        """
        self.level_score = 0
        self.player.score += (self.level_score + round((1000 * self.level) / self.get_game_time()) * (self.life_count + 1))
        return self.player.score

    def on_draw(self):
        """
        This is the display feature. The real logic is in on_update
        """
        arcade.start_render()

        # Draw all the sprites
        self.background.draw()
        self.walls.draw()
        self.coins.draw()
        self.goals.draw()
        self.enemies.draw()

        # Not all maps have ladders
        if self.ladders is not None:
            self.ladders.draw()

        # Not all maps have traps
        if self.traps is not None:
            self.traps.draw()

        # Draw the dynamic elements : play, score, life count
        self.player_sprite.draw()
        arcade.draw_rectangle_filled((SCREEN_WIDTH / 2) + self.view_left, 625 + self.view_bottom, SCREEN_WIDTH, 50, arcade.color.BLACK)
        self.draw_score()
        self.draw_life_count()
        self.draw_timer()

    def draw_score(self):
        """
        Draw the score in the top left
        """
        # First set a black background for a shadow effect
        arcade.draw_text(
            "Score:",
            start_x=600 + self.view_left,
            start_y=615 + self.view_bottom,
            color=arcade.csscolor.RED,
            font_size=self.font_size 
        )
        # Now in white, slightly shifted
        arcade.draw_text(
            "Score:",
            start_x=602 + self.view_left,
            start_y=615 + self.view_bottom,
            color=arcade.csscolor.WHITE,
            font_size=self.font_size 
        )

        arcade.draw_text(
            str(self.level_score),
            start_x=700 + self.view_left,
            start_y=615 + self.view_bottom,
            color=arcade.csscolor.RED,
            font_size=self.font_size 
        )
        # Now in white, slightly shifted
        arcade.draw_text(
            str(self.level_score),
            start_x=702 + self.view_left,
            start_y=615 + self.view_bottom,
            color=arcade.csscolor.WHITE,
            font_size=self.font_size 
        )

        # First set a black background for a shadow effect
        arcade.draw_text(
            "Total:",
            start_x=750 + self.view_left,
            start_y=615 + self.view_bottom,
            color=arcade.csscolor.RED,
            font_size=self.font_size 
        )
        # Now in white, slightly shifted
        arcade.draw_text(
            "Total:",
            start_x=752 + self.view_left,
            start_y=615 + self.view_bottom,
            color=arcade.csscolor.WHITE,
            font_size=self.font_size 
        )

        arcade.draw_text(
            str(self.player.score),
            start_x=850 + self.view_left,
            start_y=615 + self.view_bottom,
            color=arcade.csscolor.RED,
            font_size=self.font_size 
        )
        # Now in white, slightly shifted
        arcade.draw_text(
            str(self.player.score),
            start_x=852 + self.view_left,
            start_y=615 + self.view_bottom,
            color=arcade.csscolor.WHITE,
            font_size=self.font_size 
        )

    def draw_life_count(self):
        """
        Display the life count on the bottom left after the score
        """
        arcade.draw_text(
            "Lives:",
            start_x=905 + self.view_left,
            start_y=615 + self.view_bottom,
            color=arcade.csscolor.RED,
            font_size=self.font_size 
        )
        # Now in white, slightly shifted
        arcade.draw_text(
            "Lives:",
            start_x=907 + self.view_left,
            start_y=615 + self.view_bottom,
            color=arcade.csscolor.WHITE,
            font_size=self.font_size
        )

        arcade.draw_text(
            str(self.life_count),
            start_x=980 + self.view_left,
            start_y=615 + self.view_bottom,
            color=arcade.csscolor.RED,
            font_size=self.font_size 
        )
        # Now in white, slightly shifted
        arcade.draw_text(
            str(self.life_count),
            start_x=982 + self.view_left,
            start_y=615 + self.view_bottom,
            color=arcade.csscolor.WHITE,
            font_size=self.font_size 
        )


    def draw_timer(self):
        """
        Display the game timer on the bottom left after the life count
        """
        # First set a black background for a shadow effect
        arcade.draw_text(
            self.player.name + " - Level: " + str(self.level) + " - Time:",
            start_x=30 + self.view_left,
            start_y=615 + self.view_bottom,
            color=arcade.csscolor.RED,
            font_size=self.font_size 
        )
        # Now in white, slightly shifted
        arcade.draw_text(
            self.player.name + " - Level: " + str(self.level) + " - Time:",
            start_x=32 + self.view_left,
            start_y=615 + self.view_bottom,
            color=arcade.csscolor.WHITE,
            font_size=self.font_size 
        )

        # Draw the timer in the lower left, after the score
        timer_text = str(self.get_game_time())

        arcade.draw_text(
            str(timer_text),
            start_x=260 + self.view_left,
            start_y=615 + self.view_bottom,
            color=arcade.csscolor.RED,
            font_size=self.font_size 
        )
        # Now in white, slightly shifted
        arcade.draw_text(
            str(timer_text),
            start_x=262 + self.view_left,
            start_y=615 + self.view_bottom,
            color=arcade.csscolor.WHITE,
            font_size=self.font_size 
        )

    def handle_voice_command(self):
        if not self.speech_recognition.message_queue.empty():
            message = self.speech_recognition.message_queue.get()
            if(message=="jump"):
                self.player.jump()
            elif(message=="right"):
                self.player.move_right()
            elif(message=="left"):
                self.player.move_left()
            elif(message=="up"):
                self.player.move_up()
            elif(message=="down"):
                self.player.move_down()
            elif(message=="stop"):
                self.player.reset_change_x()
                if self.physics_engine.is_on_ladder():
                    self.player.reset_change_y()
    
    def create_enemy_sprites(self) -> arcade.SpriteList:
        """Creates enemy sprites appropriate for the current level

        Returns:
            A Sprite List of enemies"""
        enemies = arcade.SpriteList()

        if self.level == 2:
            enemies.append(Enemy(PLAYER_START_X + 900, PLAYER_START_Y + 64, "asteroid"))

        return enemies