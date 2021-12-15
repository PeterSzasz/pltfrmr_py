from typing import Any, Optional

class GameLogic:
    def __init__(self, actual_level = 1) -> None:
        self.actual_level = actual_level
        self.max_level = 2
        self.health = 100
        self.lives_left = 3

    def is_next_level(self):
        if self.actual_level + 1 > self.max_level:
            return False
        return True
        
    def next_level(self):
        self.actual_level += 1
        return self.actual_level

    def harm(self, injury):
        self.health -= injury
        
    def is_dead(self):
        if self.health <= 0:
            return True
        return False