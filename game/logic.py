# handles game related properties, input mode, etc

from typing import Any, Optional
from game.input import KeyboardInput, ControllerInput

class GameLogic:
    def __init__(self) -> None:
        self.health = 100
        self.lives_left = 3
        self.options = {"control":["keyboard","controller"],
                        "difficulty":["easy","medium","hard"],
                        "start level":["1","2"],
                        "debug":["true","false"]
                        }
        # TODO: read properties from file also, here
        self.actual_level = 1
        self.max_level = len(self.options["start level"])
        self.min_diff = 1   # 1:easy 2:medium 3:hard
        self.max_diff = len(self.options["difficulty"])
        self.difficulty = self.min_diff
        self.debug = True
        self.control_mode = 0
        if self.options["control"][self.control_mode] == "keyboard":
            self.input = KeyboardInput()
        else:
            self.input = ControllerInput()

    def is_next_level(self):
        if self.actual_level + 1 > self.max_level:
            return False
        return True
        
    def next_level(self):
        self.actual_level += 1
        return self.actual_level

    def shift_diffciulty(self):
        self.difficulty += 1
        if self.difficulty > self.max_diff:
            self.difficulty = self.min_diff

    def shift_player_input(self):
        self.control_mode += 1
        if self.control_mode >= len(self.options["control"]):
            self.control_mode = 0
        if self.options["control"][self.control_mode] == "keyboard":
            self.input = KeyboardInput()
        else:
            self.input = ControllerInput()

    def harm(self, injury):
        self.health -= injury
        
    def is_dead(self):
        if self.health <= 0:
            return True
        return False