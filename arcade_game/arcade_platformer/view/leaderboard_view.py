import arcade

from arcade_game.arcade_platformer.config.config import SCREEN_WIDTH, SCREEN_HEIGHT, ASSETS_PATH
from . import welcome_view, player_name_view
from arcade_game.arcade_platformer.player.player import Player
from arcade_game.arcade_platformer.helpers.speech_recognition import SpeechRecognition
import arcade.gui as gui
from arcade import load_texture
from arcade_game.arcade_platformer.utils.leaderboard import Leaderboard

class LeaderboardView(arcade.View):
    """
    Displays the Leaderboard and the ability to restart the game by pressing Enter
    """

    def __init__(self, player: Player, speech_recognition: SpeechRecognition) -> None:
        super().__init__()

        self.sound = None
        self.player = player
        self.speech_recognition = speech_recognition

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
        
        self.manager = gui.UIManager()
        self.manager.enable()
        self.leaderboard = Leaderboard()
        self.leaderboard.add_score(name=self.player.name, score=self.player.score)
        self.leaderboard.save()
        self.bg_tex = load_texture(":resources:gui_basic_assets/window/grey_panel.png")

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
        
        self.display_leaderboard()

    def display_leaderboard(self):
        text_area = gui.UITextArea(x=100,
                               y=200,
                               width=400,
                               height=500,
                               font_name="Kenney Future",
                               font_size=16,
                               text=self.leaderboard.get_as_text(),
                               text_color=(0, 0, 0, 255))
        
        self.manager.add(arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=gui.UITexturePane(
                text_area.with_space_around(right=5),
                tex=self.bg_tex,
                padding=(3, 3, 3, 3)
            )))
        
    def check_message_queue(self):
        if not self.speech_recognition.message_queue.empty():
            message = self.speech_recognition.message_queue.get()
            if(message=="start"):
                 self.start_game()
            if(message=="menu"):
                self.show_menu()

    def start_game(self):
        # Launch Enter Player Name view
        _player_name_view = player_name_view.PlayerNameView(self.player, self.speech_recognition)
        self.window.show_view(_player_name_view)

    def show_menu(self):
        _welcome_view = welcome_view.WelcomeView(self.player, self.speech_recognition)
        self.window.show_view(_welcome_view)

    def on_key_press(self, key: int, modifiers: int):
        """Restarts the game when the user presses the enter key

        Arguments:
            key -- Which key was pressed
            modifiers -- What modifiers were active
        """
        if key == arcade.key.RETURN:
            # Stop Game Over music
            self.sound.stop(self.sound_player)

            # Re-launch the game
            self.start_game()
        if key == arcade.key.BACKSPACE:
            self.sound.stop(self.sound_player)
            self.show_menu()