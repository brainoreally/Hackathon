import arcade

from arcade_game.arcade_platformer.config.config import SCREEN_WIDTH, SCREEN_HEIGHT, ASSETS_PATH
from . import platform_view
from arcade_game.arcade_platformer.player.player import Player
from arcade_game.arcade_platformer.helpers.speech_recognition import SpeechRecognition
import arcade.gui as gui
from arcade import load_texture

class PlayerNameView(arcade.View):
    """
    Displays a text entry box to accept the player name
    """

    def __init__(self, player: Player, speech_recognition: SpeechRecognition) -> None:
        super().__init__()

        self.player = player
        
        self.speech_recognition = speech_recognition

        self.game_view = None

        # Find the title image in the images folder
        title_image_path = ASSETS_PATH / "images" / "welcome.png"  # TODO change

        # Load our title image
        self.title_image = arcade.load_texture(title_image_path)

        # Set our display timer
        self.display_timer = 2.0

        self.manager = None
        self.draw_enter_player_name()

    def on_update(self, delta_time: float) -> None:
        """
        Arguments:
            delta_time -- time passed since last update
        """

        pass

    def on_draw(self) -> None:
        # Start the rendering loop
        self.clear()
        arcade.start_render()

        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        self.manager.draw()

    '''
    def on_key_press(self, key: int, modifiers: int) -> None:
        print('key pressed')
        """Start the game when the user presses the enter key

        Arguments:
            key -- Which key was pressed
            modifiers -- What modifiers were active
        """
        if key == arcade.key.RETURN:
            
            # Launch Game view
            self.game_view = platform_view.PlatformerView(self.player)
            self.game_view.setup()
            self.window.show_view(self.game_view)
'''

    def draw_enter_player_name(self):
        """
        """
       
        self.manager = gui.UIManager()
        self.manager.enable()
        # Create a text label
        self.player_name_label = arcade.gui.UILabel(
            text="Enter Player Name",
            text_color=arcade.color.DARK_RED,
            width=350,
            height=40,
            font_size=16,
            font_name="Kenney Future")

        bg_tex = load_texture(":resources:gui_basic_assets/window/grey_panel.png")
        # Create an text input field
        self.player_name_input_field = arcade.gui.UIInputText(
          text_color=arcade.color.DARK_RED,
          font_size=16,
          width=200,
          height=40,
          text='')
        
        enter_label = arcade.gui.UILabel(
            text="Then hit <ENTER> to start the game",
            text_color=arcade.color.DARK_RED,
            #width=350,
            height=40,
            font_size=16,
            font_name="Kenney Future")
        
        tp = gui.UITexturePane(
                self.player_name_input_field,
                tex=bg_tex,
                padding=(2, 2, 2, 2)
            )
        
        self.v_box = gui.UIBoxLayout()
        self.v_box.add(self.player_name_label.with_space_around(bottom=0))
        self.v_box.add(tp)
        self.v_box.add(enter_label)
        
        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box)
        )

        self.manager.draw()

    def update_text(self):
        #print(f"updating the label with input text '{self.player_name_input_field.text}'")
        self.player.name = self.player_name_input_field.text

    def launch_game(self):
        # Launch Game view
        self.game_view = platform_view.PlatformerView(self.player, self.speech_recognition)
        self.game_view.setup()
        self.window.show_view(self.game_view)

    def on_click(self, event):
        print(f"click-event caught: {event}")
        self.update_text()
        self.launch_game()

    def on_key_press(self, key: int, modifiers: int) -> None:
        """Start the game when the user presses the enter key

        Arguments:
            key -- Which key was pressed
            modifiers -- What modifiers were active
        """
        self.update_text()
        if key == arcade.key.RETURN:
            self.launch_game()