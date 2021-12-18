# game hero,enemies and other actors

from typing import Tuple
from arcade import AnimatedWalkingSprite, load_sound, load_texture, FACE_RIGHT
from arcade.sprite import FACE_LEFT

JUMPING = 5     # in continuation of FACE_UP, FACE_DOWN
SCALE = 2.0

class MainActor(AnimatedWalkingSprite):
    """The player character."""

    def __init__(self, input_subject=None) -> None:
        super().__init__()
        if input_subject:   # for this observer
            input_subject.push_handlers(self)
        self.player_jump_snd = load_sound(":resources:sounds/jump5.wav")
        self.char_img = "assets/characters/forest_characters.png"
        self.VERTICAL_SPEED = 1
        self.HORIZONTAL_SPEED = 3
        self.JUMP_SPEED = 13
        self.FRICTION = 1.0
        self.DAMPING = 0.4
        self.MASS = 2.0
        self.MAX_H_SPEED = 450
        self.MAX_V_SPEED = 1600
        self.on_ladder = False
        self.load_textures()
        self.reset_player()

    def reset_player(self):
        '''reset character to start position'''
        self.bottom = 250
        self.left = 100
        self.texture = self.walk_right_textures[0]

    def setup_subject(self, input_subject):
        input_subject.push_handlers(self)

    def load_textures(self) -> None:
        
        walking_right = [
            load_texture(self.char_img, 0+frame, 0, 32, 32) for frame in range(0, 97, 32)
        ]
        walking_left = [
            load_texture(self.char_img, 0+frame, 0, 32, 32, flipped_horizontally=True) for frame in range(0, 97, 32)
        ]
        climbing = [
            load_texture(self.char_img, 18*32+frame, 0, 32, 32) for frame in range(0, 97, 32)
        ]
        self.stand_right_textures = [walking_right[0]]
        self.stand_left_textures = [walking_left[0]]
        self.walk_right_textures = walking_right
        self.walk_left_textures = walking_left
        self.walk_up_textures = climbing
        self.walk_down_textures = climbing
        self.texture = walking_right[0]
        self._set_scale(SCALE)
        self.update_animation()

    def on_update(self, delta_time: float = 1/60) -> None:
        self.update_animation(delta_time)
        return super().on_update(delta_time=delta_time)

    def stop(self):
        self.change_x = 0
        self.change_y = 0
        
    def jump(self):
        self.change_y = self.JUMP_SPEED * SCALE * 0.7 # to compensate scale

    def move_up(self, moving):
        if moving:
            self.change_y = self.VERTICAL_SPEED * SCALE
        else:
            self.change_y = 0

    def move_down(self, moving):
        if moving:
            self.change_y = -self.VERTICAL_SPEED * SCALE
        else:
            self.change_y = 0

    def move_right(self, moving):
        if moving:
            self.change_x = self.HORIZONTAL_SPEED * SCALE
        else:
            self.change_x = 0

    def move_left(self, moving):
        if moving:
            self.change_x = -self.HORIZONTAL_SPEED * SCALE
        else:
            self.change_x = 0

class Enemy(AnimatedWalkingSprite):
    """For enemies. Walking between two obstacles."""

    def __init__(self, center_x: float, center_y: float):
        super().__init__(scale=SCALE, center_x=center_x, center_y=center_y)
        self.texture_file = "assets/characters/bloodSkeleton_character_sheet.png"
        self.load_textures()
        self.damage = 0

    def set_damage(self, damage=0):
        self.damage = damage

    def load_textures(self):
        walking_right = [
            load_texture(self.texture_file, 32+frame, 0, 32, 64) for frame in range(0, 161, 32)
        ]
        walking_left = [
            load_texture(self.texture_file, 32+frame, 0, 32, 64, flipped_horizontally=True) for frame in range(0, 161, 32)
        ]
        self.stand_right_textures = [load_texture(self.texture_file,
                                                0,
                                                0,
                                                32,
                                                64)]
        self.stand_left_textures = [load_texture(self.texture_file,
                                                0,
                                                0,
                                                32,
                                                64,
                                                flipped_horizontally=True)]
        self.walk_right_textures = walking_right
        self.walk_left_textures = walking_left
        self.texture = walking_right[1]
        self.change_x = 2
        self._set_scale(SCALE)
        self.update_animation()

    def draw(self, *, filter=None, pixelated=None, blend_function=None):
        super().draw(filter=filter, pixelated=pixelated, blend_function=blend_function)

    def on_update(self, delta_time: float = 1/60) -> None:
        self.update_animation(delta_time)
        super().on_update(delta_time=delta_time)


class EnemyFactory():
    def __init__(self) -> None:
        self.level_mul = 0
        self.no_enemies = 0
        self.base_damage = 0

    def get_enemy(self, pos: Tuple) -> Enemy:
        if pos is not None:
            new_enemy = Enemy(center_x=pos[0],center_y=pos[1])
        else:
            new_enemy = Enemy(0.0,0.0)
        new_enemy.set_damage(self.base_damage)
        return new_enemy

class EasyEnemies(EnemyFactory):
    def __init__(self) -> None:
        super().__init__()
        self.level_mul = 1
        self.no_enemies = 3
        self.base_damage = 3

        
class MediumEnemies(EnemyFactory):
    def __init__(self) -> None:
        super().__init__()
        self.level_mul = 2
        self.no_enemies = 5
        self.base_damage = 5


class HardEnemies(EnemyFactory):
    def __init__(self) -> None:
        super().__init__()
        self.level_mul = 3
        self.no_enemies = 6
        self.base_damage = 7