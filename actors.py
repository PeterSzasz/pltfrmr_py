# game hero,enemies and other actor

from random import seed,randint,choice
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

    def __init__(self, center_x: float, center_y: float, file_format: dict):
        super().__init__(scale=SCALE, center_x=center_x, center_y=center_y)
        self.texture_file = "assets/characters/"+file_format["file"]
        self.load_textures(w=file_format["width"],
                           h=file_format["height"],
                           f=file_format["frames"]
                           )
        self.damage = 0

    def set_damage(self, damage=0):
        self.damage = damage

    def load_textures(self,w,h,f):
        walking_right = [
            load_texture(self.texture_file, 0+frame, 0, w, h, flipped_horizontally=True) for frame in range(0, w*f, w)
        ]
        walking_left = [
            load_texture(self.texture_file, 0+frame, 0, w, h) for frame in range(0, w*f, w)
        ]
        self.stand_right_textures = [load_texture(self.texture_file,
                                                0,
                                                0,
                                                w,
                                                h)]
        self.stand_left_textures = [load_texture(self.texture_file,
                                                0,
                                                0,
                                                w,
                                                h,
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
        self.enemies = [{"file":"bat_black.png","frames":5,"width":32,"height":32},
                        {"file":"bat_brown.png","frames":5,"width":32,"height":32},
                        {"file":"devil_red.png","frames":4,"width":32,"height":32},
                        {"file":"skeleton_sword.png","frames":4,"width":32,"height":32}
                       ]

    def get_enemy(self, pos: Tuple, debug = False) -> list:
        '''generates enemies, child classes determines the properties'''
        if debug:
            seed(17)    # random seed for debugging,testing
        new_enemies = []
        for _ in range(self.no_enemies):
            if pos is not None:
                x=randint(pos[0]-200,pos[0]+200)
                y=randint(pos[0]-200,pos[0]+200)
                file_format = choice(self.enemies)
                print(file_format)
                new_enemy = Enemy(center_x=x,center_y=y,file_format=file_format)
                new_enemy.set_damage(self.base_damage)
                new_enemies.append(new_enemy)
            else:
                new_enemy = Enemy(0.0,0.0)
                new_enemies.append(new_enemy)
        return new_enemies

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