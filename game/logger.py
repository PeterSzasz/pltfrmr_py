# movement logger class

import time
import json

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
        if self.logging:
            tmp = {"event": "start_level", "param": None, "time": self.start_time}
            self.movement_log.append(tmp)
        print(f"START level: {self.start_time:.2f}")

    def end_level(self):
        timestamp = time.time()-self.start_time
        if self.logging:
            tmp = {"event": "end_level", "param": None, "time": timestamp}
            self.movement_log.append(tmp)
            with open("movement.json", 'w') as logfile:
                json.dump(self.movement_log, logfile, indent=2)
        print(f"END level: {timestamp:.2f}")

    def jump(self):
        timestamp = time.time()-self.start_time
        if self.logging:
            tmp = {"event": "jump", "param": None, "time": timestamp}
            self.movement_log.append(tmp)
        print(f"JUMP up: {timestamp:.2f}")

    def jetpack(self, gravity):
        timestamp = time.time()-self.start_time
        if self.logging:
            tmp = {"event": "jetpack", "param": gravity, "time": timestamp}
            self.movement_log.append(tmp)
        print(f"Jetpack ({gravity}): {timestamp:.2f}")

    def move_up(self, moving):
        timestamp = time.time()-self.start_time
        if self.logging:
            tmp = {"event": "move_up", "param": moving, "time": timestamp}
            self.movement_log.append(tmp)
        if moving:
            print(f"UP true: {timestamp:.2f}")
        else:
            print(f"UP false: {timestamp:.2f}")

    def move_down(self, moving):
        timestamp = time.time()-self.start_time
        if self.logging:
            tmp = {"event": "move_down", "param": moving, "time": timestamp}
            self.movement_log.append(tmp)
        if moving:
            print(f"DOWN true: {timestamp:.2f}")
        else:
            print(f"DOWN false: {timestamp:.2f}")

    def move_right(self, moving):
        timestamp = time.time()-self.start_time
        if self.logging:
            tmp = {"event": "move_right", "param": moving, "time": timestamp}
            self.movement_log.append(tmp)
        if moving:
            print(f"RIGHT true: {timestamp:.2f}")
        else:
            print(f"RIGHT false: {timestamp:.2f}")

    def move_left(self, moving):
        timestamp = time.time()-self.start_time
        if self.logging:
            tmp = {"event": "move_left", "param": moving, "time": timestamp}
            self.movement_log.append(tmp)
        if moving:
            print(f"LEFT true: {timestamp:.2f}")
        else:
            print(f"LEFT false: {timestamp:.2f}")