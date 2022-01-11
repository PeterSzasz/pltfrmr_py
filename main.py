# main file of a platformer

from typing import NamedTuple
from arcade import Window, run
from game.states import BaseState, MainMenu
from game.logic import GameLogic
from actors import MainActor

class Context(NamedTuple):
    window: Window
    game_logic: GameLogic
    player: MainActor

if __name__ == "__main__":
    title = "Pltfrmr 0.4"
    width = 1680
    height = 1000
    window = Window(width=width,
                    height=height,
                    title=title,
                    fullscreen=False,
                    antialiasing=False,
                    center_window=True)
    game_logic = GameLogic()
    player = MainActor()
    context = Context(window, game_logic, player)
    BaseState(context).set_next_state(MainMenu())
    run()