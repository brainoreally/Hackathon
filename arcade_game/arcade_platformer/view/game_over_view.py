import arcade

from arcade_game.arcade_platformer.config.config import SCREEN_WIDTH, SCREEN_HEIGHT, ASSETS_PATH
from . import platform_view, game_over_leaderboard_view
from arcade_game.arcade_platformer.player.player import Player
from arcade_game.arcade_platformer.helpers.speech_recognition import SpeechRecognition

class GameOverView(arcade.View):
    """
    Displays the game over screen, with the ability to restart the game by pressing Enter

    Displays a background image, play a sounds and wait for pressing the Enter key to restart the game.
    You do not have to modify these to complete the mandatory challenges.
    """

    def __init__(self, player: Player, speech_recognition: SpeechRecognition) -> None:
        super().__init__()

        self.player = player
        self.speech_recognition = speech_recognition

        # Load and play Game over music
        self.game_over_sound = arcade.load_sound(
            str(ASSETS_PATH / "sounds" / "game_over.wav")
        )
        # Play the game over sound
        self.sound_player = self.game_over_sound.play(volume=0.3)

        # Find the game over image in the images folder
        game_over_image_path = ASSETS_PATH / "images" / "game_over.png"

        # Load our game over image
        self.game_over_image = arcade.load_texture(game_over_image_path)

        # Set our display timer
        self.display_timer = 2.0

        # Are we showing the instructions?
        self.show_instructions = False

        # Reset the viewport, necessary if we have a scrolling game, and we need
        # to reset the viewport back to the start, so we can see what we draw.
        arcade.set_viewport(0, SCREEN_WIDTH - 1, 0, SCREEN_HEIGHT - 1)

    def on_update(self, delta_time: float) -> None:
        """Manages the timer to toggle the instructions

        Arguments:
            delta_time -- time passed since last update
        """

        # First, count down the time
        self.display_timer -= delta_time

        # If the timer has run out, we toggle the instructions
        if self.display_timer < 0:
            # Toggle whether to show the instructions
            self.show_instructions = not self.show_instructions

            # And reset the timer so the instructions flash slowly
            self.display_timer = 1.0

    def on_draw(self) -> None:
        self.clear()
        # Start the rendering loop
        arcade.start_render()

        # Draw a rectangle filled with our title image
        arcade.draw_texture_rectangle(
            center_x=SCREEN_WIDTH / 2,
            center_y=SCREEN_HEIGHT / 2,
            width=SCREEN_WIDTH,
            height=SCREEN_HEIGHT,
            texture=self.game_over_image,
        )

        # Should we show our instructions?
        if self.show_instructions:
            arcade.draw_text(
                #"Press Enter to start again.",
                "Press Enter to see leaderboard.",
                start_x=320,
                start_y=120,
                color=arcade.color.INDIGO,
                font_size=25,
            )
        

    def on_key_press(self, key: int, modifiers: int) -> None:
        """Restarts the game when the user presses the enter key

        Arguments:
            key -- Which key was pressed
            modifiers -- What modifiers were active
        """
        if key == arcade.key.RETURN:
            # Stop Game Over music
            self.game_over_sound.stop(self.sound_player)

            # Re-launch the game
            game_view = game_over_leaderboard_view.GameOverLeaderboardView(self.player, self.speech_recognition)
            self.window.show_view(game_view)

