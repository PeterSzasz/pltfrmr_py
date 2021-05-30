from arcade import AnimatedWalkingSprite, load_sound, load_texture, FACE_RIGHT

JUMPING = 5     # in continuation of FACE_UP, FACE_DOWN

class MainActor(AnimatedWalkingSprite):
    """The player character."""

    def __init__(self) -> None:
        super().__init__()
        self.char_img = "assets/characters/forest_characters.png"
        self.SCALE = 2.0
        self.VERTICAL_SPEED = 1
        self.HORIZONTAL_SPEED = 3
        self.JUMP_SPEED = 13
        # load textures
        self.load_textures()
        # character start position
        self.bottom = 100
        self.left = 100
        # sound business
        self.player_jump_snd = load_sound(":resources:sounds/jump5.wav")

    def load_textures(self) -> None:
        
        walking_right = [
            load_texture(self.char_img, 0+frame, 32, 32, 32) for frame in range(0, 97, 32)
        ]
        walking_left = [
            load_texture(self.char_img, 0+frame, 32, 32, 32, flipped_horizontally=True) for frame in range(0, 97, 32)
        ]
        climbing = [
            load_texture(self.char_img, 18*32+frame, 32, 32, 32) for frame in range(0, 97, 32)
        ]
        self.stand_right_textures = [walking_right[0]]
        self.stand_left_textures = [walking_left[0]]
        self.walk_right_textures = walking_right
        self.walk_left_textures = walking_left
        self.walk_up_textures = climbing
        self.walk_down_textures = climbing
        self.texture = walking_right[0]
        self._set_scale(self.SCALE)
        self.update_animation()
        self.state = JUMPING

    def update(self) -> None:
        """Update its movement, state, etc."""
        super().update()

    def on_update(self, delta_time: float = 1/60) -> None:
        self.update_animation(delta_time)
        #print(self.state)
        return super().on_update(delta_time=delta_time)

    def jump(self):
        self.change_y = self.JUMP_SPEED * self.SCALE * 0.7 # to compensate scale

    def move_up(self, moving):
        if moving:
            self.change_y = self.VERTICAL_SPEED * self.SCALE
        else:
            self.change_y = 0

    def move_down(self, moving):
        if moving:
            self.change_y = -self.VERTICAL_SPEED * self.SCALE
        else:
            self.change_y = 0

    def move_right(self, moving):
        if moving:
            self.change_x = self.HORIZONTAL_SPEED * self.SCALE
        else:
            self.change_x = 0

    def move_left(self, moving):
        if moving:
            self.change_x = -self.HORIZONTAL_SPEED * self.SCALE
        else:
            self.change_x = 0
