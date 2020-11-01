# main file of a platformer editor
# with save, load and test-play capabilities

import arcade

class MainWindow(arcade.Window):
  """
  Manages the main window of the game.
  """

  def __init__(self, width, height, title):
    """
    Initialize the main window.
    """
    super().__init__(width, height, title)

    # set background color
    arcade.set_background_color(arcade.color.GREEN)

  def on_draw(self):
    """
    called to draw in window
    """
    # clear screen
    arcade.start_render()
    # drav something
    arcade.draw_circle_filled(100, 200, 100, arcade.color.ZAFFRE)


def main():
  
  print("Game Started.")
  mwin = MainWindow(1000, 500, "Pltfrmr v0.1")
  arcade.run()


if __name__ == "__main__":
  main()