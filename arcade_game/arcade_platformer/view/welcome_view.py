import arcade
from threading import Thread

from arcade_game.arcade_platformer.config.config import SCREEN_WIDTH, SCREEN_HEIGHT, ASSETS_PATH
from . import winning_leaderboard_view, player_name_view
from arcade_game.arcade_platformer.player.player import Player
from arcade_game.arcade_platformer.helpers.speech_recognition import SpeechRecognition
from log.config_log import logger


class WelcomeView(arcade.View):
    """
    Displays a welcome screen and prompts the user to begin the game.

    Displays a background image, play a sounds and wait for pressing the Enter key to start the game.
    You do not have to modify these to complete the mandatory challenges.
    """

    def __init__(self, player: Player, speech_recognition: SpeechRecognition) -> None:
        super().__init__()

        self.player = player

        self.speech_recognition = speech_recognition

        self.game_view = None

        # Load & play intro music
        self.intro_sound = arcade.load_sound(
            str(ASSETS_PATH / "sounds" / "intro.wav")
        )
        self.sound_player = self.intro_sound.play(volume=0, loop=True)

        # Find the title image in the images folder
        title_image_path = ASSETS_PATH / "images" / "welcome.png"

        # Load our title image
        self.title_image = arcade.load_texture(title_image_path)

        # Set our display timer
        self.display_timer = 2.0

        # Are we showing the instructions?
        self.show_instructions = False

    def check_message_queue(self):
        if not self.speech_recognition.message_queue.empty():
            message = self.speech_recognition.message_queue.get()
            logger.info(f"welcome view message {message}")
            if(message=="start"):
                self.start_game()
            if(message=="leaderboard"):
                self.show_leaderboard()

    def on_update(self, delta_time: float) -> None:
        """Manages the timer to toggle the instructions

        Arguments:
            delta_time -- time passed since last update
        """
        self.check_message_queue()

        # First, count down the time
        self.display_timer -= delta_time

        # If the timer has run out, we toggle the instructions
        if self.display_timer < 0:
            # Toggle whether to show the instructions
            self.show_instructions = not self.show_instructions

            # And reset the timer so the instructions flash slowly
            self.display_timer = 1.0

    def on_draw(self) -> None:
        # Start the rendering loop
        arcade.start_render()

        # Draw a rectangle filled with our title image
        arcade.draw_texture_rectangle(
            center_x=SCREEN_WIDTH / 2,
            center_y=SCREEN_HEIGHT / 2,
            width=SCREEN_WIDTH,
            height=SCREEN_HEIGHT,
            texture=self.title_image,
        )

        # Should we show our instructions?
        if self.show_instructions:
            arcade.draw_text(
                "Press enter to Start the game",
                start_x=250,
                start_y=170,
                color=arcade.color.SELECTIVE_YELLOW,
                font_size=30,
            )

    def on_key_press(self, key: int, modifiers: int) -> None:
        if key == arcade.key.RETURN:
            self.start_game()
        if key == arcade.key.L:
            self.show_leaderboard()
    
    def start_game(self) -> None:
        # Stop intro music
            self.intro_sound.stop(self.sound_player)
            # Launch Enter Player Name view
            _player_name_view = player_name_view.PlayerNameView(self.player, self.speech_recognition)
            self.window.show_view(_player_name_view)

    def show_leaderboard(self) -> None:
            _leaderboard_view = winning_leaderboard_view.WinningLeaderboardView(self.player, self.speech_recognition)
            self.window.show_view(_leaderboard_view)