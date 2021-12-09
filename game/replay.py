# re-plays a previously logged 

import time
from pyglet.event import EventDispatcher

class LogReplay(EventDispatcher):
    def __init__(self, logger) -> None:
        self.log = logger.get_log()
        self.start_time = None
        self.log_pos = 0

    def set_observer(self, player):
        player.setup_subject(self)

    def start_play(self):
        self.log_pos = 0
        self.start_time = time.time()

    def next_move(self):
        if self.start_time:
            delay = time.time() - self.start_time
            if self.log[self.log_pos][1] < delay:
                movement = self.log[self.log_pos][0]
                if movement == "jump":
                    self.dispatch_event('jump')
                if movement == "move_right True":
                    self.dispatch_event('move_right',True)
                if movement == "move_right False":
                    self.dispatch_event('move_right',False)
                if movement == "move_left True":
                    self.dispatch_event('move_left',True)
                if movement == "move_left False":
                    self.dispatch_event('move_left',False)
                if movement == "move_up True":
                    self.dispatch_event('move_up',True)
                if movement == "move_up False":
                    self.dispatch_event('move_up',False)
                if movement == "move_down True":
                    self.dispatch_event('move_down',True)
                if movement == "move_down False":
                    self.dispatch_event('move_down',False)
                if movement == "end_level":
                    print("playback end")
                    self.start_time = None
                else:
                    self.log_pos += 1


LogReplay.register_event_type('move_right')
LogReplay.register_event_type('move_left')
LogReplay.register_event_type('move_up')
LogReplay.register_event_type('move_down')
LogReplay.register_event_type('jump')
LogReplay.register_event_type('start_level')
LogReplay.register_event_type('end_level')
