# re-plays a previously logged 

import time, json
from pyglet.event import EventDispatcher

class LogReplay(EventDispatcher):
    def __init__(self, logger) -> None:
        self.log = logger.get_log()
        self.start_time = None
        self.log_pos = 0

    def set_observer(self, player):
        player.setup_subject(self)

    def start_play(self, filename=None):
        if filename:
            with open(filename, 'r') as logfile:
                self.log = json.load(logfile)
        self.log_pos = 0
        self.start_time = time.time()

    def next_move(self):
        if self.start_time:
            delay = time.time() - self.start_time
            if self.log[self.log_pos]["time"] < delay:
                movement = self.log[self.log_pos]["event"]
                param = self.log[self.log_pos]["param"]

                if movement == "end_level":
                    print("playback end")
                    self.start_time = None
                else:
                    if param is not None:
                        self.dispatch_event(movement, param)
                    else:
                        self.dispatch_event(movement)
                    self.log_pos += 1


LogReplay.register_event_type('move_right')
LogReplay.register_event_type('move_left')
LogReplay.register_event_type('move_up')
LogReplay.register_event_type('move_down')
LogReplay.register_event_type('jump')
LogReplay.register_event_type('start_level')
LogReplay.register_event_type('end_level')
