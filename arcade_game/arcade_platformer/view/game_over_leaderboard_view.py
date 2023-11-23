import arcade

from arcade_game.arcade_platformer.config.config import SCREEN_WIDTH, SCREEN_HEIGHT, ASSETS_PATH
from . import platform_view
from arcade_game.arcade_platformer.player.player import Player
from arcade_game.arcade_platformer.helpers.speech_recognition import SpeechRecognition
import arcade.gui as gui
from arcade import load_texture
from arcade_game.arcade_platformer.utils.leaderboard import Leaderboard

class GameOverLeaderboardView(arcade.View):
    """
    Displays the Leaderboard and the ability to restart the game by pressing Enter
    """

    def __init__(self, player: Player, speech_recognition: SpeechRecognition) -> None:
        super().__init__()

        self.player = player
        self.speech_recognition = speech_recognition

        # Load and play Game over music
        self.game_over_sound = arcade.load_sound(
            str(ASSETS_PATH / "sounds" / "game_over.wav")  # TODO leaderboard sound ?
        )
        # Play the game over sound
        self.sound_player = self.game_over_sound.play(volume=0.3)

        # Find the game over image in the images folder
        leaderboard_image_path = ASSETS_PATH / "images" / "leaderboard.png" 

        # Load our game over image
        self.leaderboard_image = arcade.load_texture(leaderboard_image_path)

        # Set our display timer
        self.display_timer = 2.0

        # Are we showing the instructions?
        self.show_instructions = False

        # Reset the viewport, necessary if we have a scrolling game, and we need
        # to reset the viewport back to the start, so we can see what we draw.
        arcade.set_viewport(0, SCREEN_WIDTH - 1, 0, SCREEN_HEIGHT - 1)

    def setup(self):
        self.display_leaderboard()

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
            texture=self.leaderboard_image,
        )

        # Should we show our instructions?
        if self.show_instructions:
            arcade.draw_text(
                "Press Enter to start again.",
                start_x=320,
                start_y=120,
                color=arcade.color.INDIGO,
                font_size=25,
            )
        self.manager.draw()

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
            game_view = platform_view.PlatformerView(self.player, self.speech_recognition)
            game_view.setup()
            self.window.show_view(game_view)

    def display_leaderboard(self):
        self.manager = gui.UIManager()
        self.manager.enable()
        leaderboard = Leaderboard()
        bg_tex = load_texture(":resources:gui_basic_assets/window/grey_panel.png")
        text_area = gui.UITextArea(x=100,
                               y=200,
                               width=400,
                               height=500,
                               font_name="Kenney Future",
                               font_size=16,
                               text=leaderboard.get_as_text(),
                               text_color=(0, 0, 0, 255))
        
        self.manager.add(arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=gui.UITexturePane(
                text_area.with_space_around(right=5),
                tex=bg_tex,
                padding=(3, 3, 3, 3)
            )))

        self.manager.draw()