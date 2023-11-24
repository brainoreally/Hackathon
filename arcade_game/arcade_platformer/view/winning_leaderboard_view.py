import arcade

from arcade_game.arcade_platformer.config.config import SCREEN_WIDTH, SCREEN_HEIGHT, ASSETS_PATH
from . import platform_view
from arcade_game.arcade_platformer.player.player import Player
from arcade_game.arcade_platformer.helpers.speech_recognition import SpeechRecognition
from arcade_game.arcade_platformer.view.leaderboard_view import LeaderboardView

class WinningLeaderboardView(LeaderboardView):
    """
    Displays the Leaderboard and the ability to restart the game by pressing Enter
    """

    def __init__(self, player: Player, speech_recognition: SpeechRecognition) -> None:
        super().__init__(player=player, speech_recognition=speech_recognition)

        # Load and play Game over music
        self.sound = arcade.load_sound(
            str(ASSETS_PATH / "sounds" / "victory.wav")  # TODO leaderboard sound ?
        )
        # Play the game over sound
        self.sound_player = self.sound.play(volume=0.3)
