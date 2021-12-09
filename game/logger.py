# movement logger class

import time

class MovementLogger:
    def __init__(self, input_subject=None) -> None:
        if input_subject:
            input_subject.push_handlers(self)
        self.start_time = None
        self.movement_log = []
        self.logging = True

    def setup_subject(self, input_subject):
        input_subject.push_handlers(self)

    def get_log(self):
        return self.movement_log

    def start_level(self):
        self.start_time = time.time()
        print(f"start level: {self.start_time}")

    def end_level(self):
        timestamp = time.time()-self.start_time
        print(f"end level: {timestamp}")
        if self.logging:
            self.movement_log.append(("end_level",timestamp))

    def jump(self):
        timestamp = time.time()-self.start_time
        print(f"Jump: {timestamp}")
        if self.logging:
            self.movement_log.append(("jump",timestamp))

    def move_up(self, moving):
        timestamp = time.time()-self.start_time
        if self.logging:
            self.movement_log.append((f"move_up {moving}",timestamp))
        if moving:
            print(f"UP true: {timestamp}")
        else:
            print(f"UP false: {timestamp}")

    def move_down(self, moving):
        timestamp = time.time()-self.start_time
        if self.logging:
            self.movement_log.append((f"move_down {moving}",timestamp))
        if moving:
            print(f"DOWN true: {timestamp}")
        else:
            print(f"DOWN false: {timestamp}")

    def move_right(self, moving):
        timestamp = time.time()-self.start_time
        if self.logging:
            self.movement_log.append((f"move_right {moving}",timestamp))
        if moving:
            print(f"RIGHT true: {timestamp}")
        else:
            print(f"RIGHT false: {timestamp}")

    def move_left(self, moving):
        timestamp = time.time()-self.start_time
        if self.logging:
            self.movement_log.append((f"move_left {moving}",timestamp))
        if moving:
            print(f"LEFT true: {timestamp}")
        else:
            print(f"LEFT false: {timestamp}")