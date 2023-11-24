import arcade

from arcade_game.arcade_platformer.config.config import ASSETS_PATH, PLAYER_MOVE_SPEED

class Enemy(arcade.AnimatedWalkingSprite):
    """An enemy sprite with basic walking movement"""

    def __init__(self, pos_x: int, pos_y: int, sprite_name: str) -> None:
        super().__init__(center_x=pos_x, center_y=pos_y)

        # Where are the player images stored?
        texture_path = ASSETS_PATH / "images" / "enemies"
        sprite_name_full = sprite_name + ".png"
        sprite_name_move_full = sprite_name + "_move.png"
        # Set up the appropriate textures
        walking_texture_path = [
            texture_path / sprite_name_full,
            texture_path / sprite_name_move_full,
        ]
        standing_texture_path = texture_path / sprite_name_full

        # Load them all now
        self.walk_left_textures = [
            arcade.load_texture(texture) for texture in walking_texture_path
        ]

        self.walk_right_textures = [
            arcade.load_texture(texture, mirrored=True)
            for texture in walking_texture_path
        ]

        self.stand_left_textures = [
            arcade.load_texture(standing_texture_path, mirrored=True)
        ]
        self.stand_right_textures = [
            arcade.load_texture(standing_texture_path)
        ]

        # Set the enemy defaults
        self.state = arcade.FACE_LEFT
        self.change_x = -PLAYER_MOVE_SPEED // 2

        # Set the initial texture
        self.texture = self.stand_left_textures[0]