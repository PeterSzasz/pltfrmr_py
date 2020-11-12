# main file of a platformer editor
# with save, load and test-play capabilities

import os
import arcade
from pyglet.gl import GL_NEAREST
from pyglet.gl import GL_LINEAR
from random import randint

class MainActor(arcade.Sprite):
  """The player character."""

  def __init__(self, filename: str, scale, image_x, image_y, image_width, image_height, center_x = 0, center_y = 0):
    super().__init__(filename, scale, image_x, image_y, image_width, image_height, center_x, center_y)

  def update(self):
    """Update its movement, state, etc."""
    super().update()

  def jump(self, jump_speed):
    self.change_y = jump_speed

  def move_up(self, moving):
    if moving:
      self.change_y = 5
    else:
      self.change_y = 0

  def move_down(self, moving):
    if moving:
      self.change_y = -5
    else:
      self.change_y = 0

  def move_right(self, moving):
    if moving:
      self.change_x = 5
    else:
      self.change_x = 0

  def move_left(self, moving):
    if moving:
      self.change_x = -5
    else:
      self.change_x = 0


class MainWindow(arcade.Window):
  """
  Manages the main window of the game.
  """

  def __init__(self, title, width = 1000, height = 500):
    super().__init__(width, height, title)
    self.SCREEN_WIDTH = width
    self.SCREEN_HEIGHT = height
    self.initial_setup()

  def initial_setup(self):
    """Initializes the main window. Handles keyb input. Renders."""
    # set background color
    arcade.set_background_color(arcade.color.LIGHT_MOSS_GREEN)
    # viewwport settings
    self.LEFT_VIEW_MARGIN = 100
    self.RIGHT_VIEW_MARGIN = 100
    self.BOTTOM_VIEW_MARGIN = 50
    self.TOP_VIEW_MARGIN = 50
    self.viewport_left = 0
    self.viewport_bottom = 0

    # sound business
    self.player_jump_snd = arcade.load_sound(":resources:sounds/jump5.wav")

    # what follows are game world things, should go into separate class, when fat
    # Set up the empty sprite lists
    self.enemies_list = arcade.SpriteList()
    self.coins_list = arcade.SpriteList()
    self.walls_list = arcade.SpriteList(use_spatial_hash=True)
    self.ladders_list = arcade.SpriteList(use_spatial_hash=True)
    self.all_sprites = arcade.SpriteList()
    
    # texts
    self.static_text = "Alderaan VI"
    self.dinamy_text = "Score: "
    self.coin_point = 0
    self.MIN_COIN = 5
    self.MAX_COIN = 8

    # add player
    self.base_dir = os.path.dirname(__file__)
    self.player = MainActor(self.base_dir + "/assets/forest_characters.png", 1, 0, 32, 32, 32)
    self.player.bottom = 96
    self.player.left = 100
    self.all_sprites.append(self.player)

    # add base platform bricks
    for y in range(0, 33, 32):
      for x in range(0, 1800, 32):
        rand_x_offset = randint(0, 3)
        rand_y_offset = randint(0, 3)
        brick_sprite = arcade.Sprite(self.base_dir + "/assets/blocksteel_sheet.png", 2, 80 + (16 * rand_x_offset), 80 + (16 * rand_y_offset), 16, 16)
        brick_sprite.bottom = 0 + y
        brick_sprite.left = 0 + x
        self.walls_list.append(brick_sprite)
    # random jump platform bricks
    for i in range(5, 40, 1):
      rand_x_offset = randint(0, 3)
      rand_y_offset = randint(0, 3)
      brick_sprite = arcade.Sprite(self.base_dir + "/assets/blocksteel_sheet.png", 2, 80 + (16 * rand_x_offset), 8 + (16 * rand_y_offset), 16, 16)
      brick_sprite.bottom = 96 + randint(0, 10) * 32
      brick_sprite.left = 32 + randint(1,80) * 32
      self.walls_list.append(brick_sprite)
    # plapce coins randomly
    for j in range(self.MIN_COIN, self.MAX_COIN, 1):
      coin_sprite = arcade.Sprite(":resources:images/items/coinGold.png", 0.25, 0, 0, 128, 128)
      coin_sprite.bottom = 96 + randint(0, 10) * 32
      coin_sprite.left = 32 + randint(1,80) * 32
      self.coins_list.append(coin_sprite)
    
    # turn on physics engine
    self.GRAVITY = 1
    self.PLAYER_JUMP_SPEED = 20
    self.physics_engine = arcade.PhysicsEnginePlatformer(self.player, self.walls_list, self.GRAVITY, self.ladders_list)

  def on_draw(self):
    """called to draw in window"""
    arcade.start_render()
    
    #draw assets and sprites
    arcade.draw_circle_filled(900, 450, 25, arcade.color.YELLOW_ORANGE)
    self.walls_list.draw(filter = GL_LINEAR)
    self.coins_list.draw()
    self.all_sprites.draw(filter = GL_LINEAR)
    
    # texts
    arcade.draw_text(self.static_text, 16, 64, arcade.color.LIGHT_BROWN, 16)
    text = self.dinamy_text + str(self.coin_point) + " <" + str(self.MIN_COIN) + " - " + str(self.MAX_COIN) + ">"
    arcade.draw_text(text, 5 + self.viewport_left, self.SCREEN_HEIGHT-20, arcade.color.LIGHT_BROWN, 12)
    
  def on_update(self, delta_time: float):
    """manage state, view updates"""
    self.all_sprites.update()
    self.physics_engine.update()

    # check for collision
    colliding_coins = arcade.check_for_collision_with_list(self.player, self.coins_list)
    for coin in colliding_coins:
      coin.remove_from_sprite_lists()
      self.coin_point += 1

    # viewport scrolling
    changed = False
    if self.player.left < self.viewport_left + self.LEFT_VIEW_MARGIN:
      self.viewport_left -= self.viewport_left + self.LEFT_VIEW_MARGIN - self.player.left
      changed = True

    if self.player.right > self.viewport_left + self.SCREEN_WIDTH - self.RIGHT_VIEW_MARGIN:
      self.viewport_left += self.player.right - (self.viewport_left + self.SCREEN_WIDTH - self.RIGHT_VIEW_MARGIN)
      changed = True

    if changed:
      self.viewport_left = int(self.viewport_left)
      self.viewport_bottom = int(self.viewport_bottom)
      arcade.set_viewport(self.viewport_left, self.SCREEN_WIDTH + self.viewport_left,
                          self.viewport_bottom, self.SCREEN_HEIGHT + self.viewport_bottom)


  def on_key_press(self, symbol: int, modifiers: int):
    """if a key is pressed.."""
    if symbol == arcade.key.UP:
      if self.physics_engine.can_jump():
        self.player.jump(self.PLAYER_JUMP_SPEED)
        arcade.play_sound(self.player_jump_snd)
      else:
        self.player.move_up(True)

    if symbol == arcade.key.DOWN:
      self.player.move_down(True)

    if symbol == arcade.key.LEFT:
      self.player.move_left(True)

    if symbol == arcade.key.RIGHT:
      self.player.move_right(True)

  def on_key_release(self, symbol: int, modifiers: int):
    """if a key is released..."""
    if symbol == arcade.key.UP:
      self.player.move_up(False)

    if symbol == arcade.key.DOWN:
      self.player.move_down(False)

    if symbol == arcade.key.LEFT:
      self.player.move_left(False)

    if symbol == arcade.key.RIGHT:
      self.player.move_right(False)


def main():
  """app entry point and main loop"""
  print("Game Started.")
  mwin = MainWindow("Pltfrmr v0.1")
  arcade.run()


if __name__ == "__main__":
  main()