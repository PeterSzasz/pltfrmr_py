# game hero,enemies and other actor

from random import seed,randint,choice
from typing import Tuple
from arcade import AnimatedWalkingSprite, load_sound, load_texture
from arcade.sprite import FACE_LEFT

JUMPING = 5     # in continuation of FACE_UP, FACE_DOWN
SCALE = 2.0


class MainActor(AnimatedWalkingSprite):
    """The player character."""

    def __init__(self, input_subject=None, burst_effect=None) -> None:
        super().__init__()
        self.burst_effect = burst_effect
        if input_subject:   # for this observer
            input_subject.push_handlers(self)
        self.player_jump_snd = load_sound(":resources:sounds/jump5.wav")
        self.char_img = "assets/characters/forest_characters.png"
        self.idle_texture = [[]]*2
        self.walk_textures = [[]]*2
        self.squat_texture = [[]]*2
        self.jump_upward_texture = [[]]*2
        self.jump_downward_texture = [[]]*2
        self.climbing_textures = [[]]*2
        self.hit_textures = [[]]*2
        self.slash_textures = [[]]*2
        self.RIGHT = 0
        self.LEFT = 1
        self.cur_texture = 0
        self.force = (0.0,0.0)
        self.impulse = (0.0,0.0)
        self.MASS = 2.0
        self.DAMPING = 0.2
        self.FRICTION = 1.0
        self.MAX_H_SPEED = 450
        self.MAX_V_SPEED = 1600
        self.MOVE_FORCE_GROUND = 6000
        self.MOVE_FORCE_AIR = 1800
        self.MOVE_FORCE_LADDER = self.MOVE_FORCE_GROUND/1.55
        self.JUMP_IMPULSE = 1300
        self.JETPACK_BURST = 200
        self.on_ladder = False
        self.on_ground = True
        self.on_jetpack = False
        self.squatting = False
        self.facing_right = True
        self.x_odometer = 0.0
        self.y_odometer = 0.0
        self.load_textures()
        self.reset_player()

    def set_burst_effect(self, burst_effect):
        if burst_effect:
            self.burst_effect = burst_effect

    def reset_player(self):
        '''reset character to start position'''
        self.bottom = 250
        self.left = 110
        self.texture = self.idle_texture[self.RIGHT][0]

    def setup_subject(self, input_subject):
        input_subject.push_handlers(self)

    def load_textures(self) -> None:
        R = self.RIGHT
        L = self.LEFT
        self.idle_texture[R] = [
            load_texture(self.char_img, 0, 0, 32, 32)    # frame 1
        ]
        self.idle_texture[L] = [
            load_texture(self.char_img, 0, 0, 32, 32, flipped_horizontally=True)    # frame 1
        ]
        self.walk_textures[R] = [    # frame 1-4
            load_texture(self.char_img, 0+frame, 0, 32, 32) for frame in range(0, 4*32, 32)
        ]
        self.walk_textures[L] = [     # frame 1-4, flipped left
            load_texture(self.char_img, 0+frame, 0, 32, 32, flipped_horizontally=True) for frame in range(0, 4*32, 32)
        ]
        self.squat_texture[R] = [
            load_texture(self.char_img, 4*32, 0, 32, 32)    # frame 5
        ]
        self.squat_texture[L] = [
            load_texture(self.char_img, 4*32, 0, 32, 32, flipped_horizontally=True)    # frame 5
        ]
        self.jump_upward_texture[R] = [
            load_texture(self.char_img, 5*32, 0, 32, 32)    # frame 6
        ]
        self.jump_upward_texture[L] = [
            load_texture(self.char_img, 5*32, 0, 32, 32, flipped_horizontally=True)    # frame 6
        ]
        self.jump_downward_texture[R] = [
            load_texture(self.char_img, 6*32, 0, 32, 32)    # frame 7
        ]
        self.jump_downward_texture[L] = [
            load_texture(self.char_img, 6*32, 0, 32, 32, flipped_horizontally=True)    # frame 7
        ]
        self.climbing_textures[R] = [      # frame 19-22
            load_texture(self.char_img, 18*32+frame, 0, 32, 32) for frame in range(0, 4*32, 32)
        ]
        self.climbing_textures[L] = [      # frame 19-22
            load_texture(self.char_img, 18*32+frame, 0, 32, 32, flipped_horizontally=True) for frame in range(0, 4*32, 32)
        ]
        self.hit_textures[R] = [
            load_texture(self.char_img, 8*32, 0, 32, 32),    # frame 9
            load_texture(self.char_img, 9*32, 0, 32, 32),    # frame 10
            load_texture(self.char_img, 8*32, 0, 32, 32)    # frame 9
        ]
        self.hit_textures[L] = [
            load_texture(self.char_img, 8*32, 0, 32, 32, flipped_horizontally=True),    # frame 9
            load_texture(self.char_img, 9*32, 0, 32, 32, flipped_horizontally=True),    # frame 10
            load_texture(self.char_img, 8*32, 0, 32, 32, flipped_horizontally=True)    # frame 9
        ]
        self.slash_textures[R] = [
            load_texture(self.char_img, 11*32, 0, 32, 32),    # frame 12, preparation
            load_texture(self.char_img, 10*32, 0, 32, 32),    # frame 11
            load_texture(self.char_img, 11*32, 0, 32, 32),    # frame 12
            load_texture(self.char_img, 12*32, 0, 32, 32)    # frame 13
        ]
        self.slash_textures[L] = [
            load_texture(self.char_img, 11*32, 0, 32, 32, flipped_horizontally=True),    # frame 12, preparation
            load_texture(self.char_img, 10*32, 0, 32, 32, flipped_horizontally=True),    # frame 11
            load_texture(self.char_img, 11*32, 0, 32, 32, flipped_horizontally=True),    # frame 12
            load_texture(self.char_img, 12*32, 0, 32, 32, flipped_horizontally=True)    # frame 13
        ]
        self.texture = self.idle_texture[R][self.cur_texture]
        self._set_scale(SCALE)

    def pymunk_moved(self, physics_engine, dx, dy, d_angle):
        """ Handle being moved by the pymunk engine """
        DEAD_ZONE = 0.5
        if dx < -DEAD_ZONE and self.facing_right is True:
            self.facing_right = False
        elif dx > DEAD_ZONE and self.facing_right is False:
            self.facing_right = True

        if self.facing_right:
            face = self.RIGHT
        else:
            face = self.LEFT

        # add how far we've moved
        self.x_odometer += dx
        self.y_odometer += dy

        # ladder
        if self.on_ladder and not self.on_ground and not self.on_jetpack:
            if abs(self.y_odometer) > 10:
                self.y_odometer = 0
                self.cur_texture += 1
            if self.cur_texture >= len(self.climbing_textures[0]):
                self.cur_texture = 0
            self.texture = self.climbing_textures[face][self.cur_texture]
            return

        # jumping
        if not self.on_ground and not self.on_ladder:
            if dy < -DEAD_ZONE:
                self.texture = self.jump_downward_texture[face][0]
                return
            elif dy > DEAD_ZONE:
                self.texture = self.jump_upward_texture[face][0]
                return

        # squatting
        if self.squatting and self.on_ground:
            self.texture = self.squat_texture[face][0]
            return

        # idle
        if abs(dx) < DEAD_ZONE:
            self.texture = self.idle_texture[face][0]
            return

        # walk
        if not self.on_jetpack and abs(self.x_odometer) > 20:
            self.x_odometer = 0
            self.cur_texture += 1
            if self.cur_texture >= len(self.walk_textures[0]):
                self.cur_texture = 0
            self.texture = self.walk_textures[face][self.cur_texture]
            
    def on_update(self, delta_time: float = 1/60) -> None:
        return super().on_update(delta_time=delta_time)

    def squat(self):
        if self.on_ground and not self.on_ladder:
            self.squatting = True
        
    def jump(self):
        self.squatting = False
        if self.on_ground and not self.on_ladder:
            self.impulse = (0.0, self.JUMP_IMPULSE)

    def jetpack(self):
        self.on_jetpack = not self.on_jetpack
        if self.on_jetpack:
            self.force = (self.force[0],2997)
            self.impulse = (0.0, self.JETPACK_BURST)

    def move_up(self, moving):
        if moving:
            if self.on_ladder:
                self.force = (0.0,self.MOVE_FORCE_LADDER)
            elif self.on_jetpack:
                self.impulse = (0.0, self.JETPACK_BURST)
                if self.burst_effect:
                    self.burst_effect.jet_burst(self.center_x, self.center_y)
        else:
            if self.on_ladder:
                self.force = (0.0,self.MOVE_FORCE_LADDER/2)
            elif not self.on_jetpack:
                self.force = (0.0,0.0)

    def move_down(self, moving):
        if moving:
            if self.on_ladder:
                self.force = (0.0,-self.MOVE_FORCE_GROUND)
            elif self.on_jetpack:
                self.impulse = (0.0, -self.JETPACK_BURST)
        elif not self.on_jetpack:
            self.force = (0.0,0.0)

    def move_left(self, moving):
        if moving:     
            if self.on_ground and not self.on_jetpack:       
                self.force = (-self.MOVE_FORCE_GROUND, 0.0)
                self.FRICTION = 0.0
            elif self.on_jetpack:
                self.impulse = (-self.JETPACK_BURST, 0.0)
            elif self.on_ladder:
                h_force = self.force[1]
                self.force = (-self.MOVE_FORCE_LADDER,h_force)
            else:
                self.force = (-self.MOVE_FORCE_AIR, 0.0)
        else:
            if self.on_ladder and not self.on_ground:
                h_force = self.force[1]
                self.force = (0.0,h_force)
            elif not self.on_jetpack:
                self.force = (0.0,0.0)
                self.FRICTION = 1.0

    def move_right(self, moving):
        if moving:
            if self.on_ground and not self.on_jetpack:      
                self.force = (self.MOVE_FORCE_GROUND, 0.0)
                self.FRICTION = 0.0
            elif self.on_jetpack:
                self.impulse = (self.JETPACK_BURST, 0.0)
            elif self.on_ladder:
                h_force = self.force[1]
                self.force = (self.MOVE_FORCE_LADDER,h_force)
            else:
                self.force = (self.MOVE_FORCE_AIR, 0.0)
        else:
            if self.on_ladder and not self.on_ground:
                h_force = self.force[1]
                self.force = (0.0,h_force)
            elif not self.on_jetpack:
                self.force = (0.0,0.0)
                self.FRICTION = 1.0


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
        self.health = 10

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