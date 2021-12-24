from typing import Any, Optional

class GameLogic:
    def __init__(self, actual_level = 1) -> None:
        self.actual_level = 2#actual_level
        self.max_level = 2
        self.health = 100
        self.lives_left = 3
        self.min_diff = 1   # 1:easy 2:medium 3:hard
        self.max_diff = 3
        self.difficulty = self.min_diff
        self.options = {"control":["keyboard","controller"],
                        "difficulty":["easy","medium","hard"],
                        "start level":["1","2","3"],
                        "debug":["true","false"]
                        }
        self.debug = True

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

    def harm(self, injury):
        self.health -= injury
        
    def is_dead(self):
        if self.health <= 0:
            return True
        return False