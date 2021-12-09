# main file of a platformer

from arcade import Window, run
from game.views import MenuView
from game.logic import GameLogic
from game.logger import MovementLogger
from actors import MainActor

class MainWindow(Window):
    def __init__(self):
        title = "Pltfrmr 0.2"
        width = 1680
        height = 1000
        super().__init__(width=width, height=height, title=title)
        self.center_window()
        self.player = MainActor()
        self.show_view(MenuView(self))
        self.logic = GameLogic()
        self.movement_logger = MovementLogger()


if __name__ == "__main__":
    MainWindow()
    run()