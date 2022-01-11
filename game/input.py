# handles kyboard or controller input

import XInput
from pyglet.event import EventDispatcher
from arcade import key as arcade_key

class BaseInput(EventDispatcher):
    def __init__(self) -> None:
        pass

    def update(self):
        pass

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        pass

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        pass

BaseInput.register_event_type('move_right')
BaseInput.register_event_type('move_left')
BaseInput.register_event_type('move_up')
BaseInput.register_event_type('move_down')
BaseInput.register_event_type('squat')
BaseInput.register_event_type('jump')
BaseInput.register_event_type('jetpack')
BaseInput.register_event_type('start_level')
BaseInput.register_event_type('end_level')


class KeyboardInput(BaseInput):
    def __init__(self) -> None:
        pass

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        if symbol == arcade_key.SPACE:
            self.dispatch_event('squat')

        if symbol == arcade_key.UP:
            self.dispatch_event('move_up',True)

        if symbol == arcade_key.DOWN:
            self.dispatch_event('move_down',True)

        if symbol == arcade_key.LEFT:
            self.dispatch_event('move_left',True)

        if symbol == arcade_key.RIGHT:
            self.dispatch_event('move_right',True)

        if symbol == arcade_key.J:
            self.dispatch_event('jetpack')

        if symbol == arcade_key.C:
            pass
            # use previously saved/set combo moves

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        if symbol == arcade_key.UP:
            self.dispatch_event('move_up',False)

        if symbol == arcade_key.DOWN:
            self.dispatch_event('move_down',False)

        if symbol == arcade_key.LEFT:
            self.dispatch_event('move_left',False)

        if symbol == arcade_key.RIGHT:
            self.dispatch_event('move_right',False)

        if symbol == arcade_key.SPACE:
            self.dispatch_event('jump')


class ControllerInput(BaseInput):
    def __init__(self) -> None:
        pass

    def update(self):
        # if gameplay active:
        for xinput_event in XInput.get_events():
            if xinput_event.user_index == 0:
                if xinput_event.type == XInput.EVENT_BUTTON_PRESSED:
                    if xinput_event.button_id == 4096 and \
                        self.physics_engine.is_on_ground(self.player) and \
                        not self.player.on_ladder:
                            self.dispatch_event('jump')
                    if xinput_event.button_id == 1:
                        self.dispatch_event('move_up',True)
                    if xinput_event.button_id == 2:
                        self.dispatch_event('move_down',True)
                    if xinput_event.button_id == 4:
                        self.dispatch_event('move_left',True)
                    if xinput_event.button_id == 8:
                        self.dispatch_event('move_right',True)
                if xinput_event.type == XInput.EVENT_BUTTON_RELEASED:
                    if xinput_event.button_id == 4096:
                        pass #self.player.stop()    # TODO: replace
                    if xinput_event.button_id == 1:
                        self.dispatch_event('move_up',False)
                    if xinput_event.button_id == 2:
                        self.dispatch_event('move_down',False)
                    if xinput_event.button_id == 4:
                        self.dispatch_event('move_left',False)
                    if xinput_event.button_id == 8:
                        self.dispatch_event('move_right',False)
        # else if menu active
        # if any(XInput.get_connected()):
        #     xinput_status = XInput.get_button_values(XInput.get_state(0))
        #     if xinput_status['A']:
        #         self.set_next_state(Gameplay(self.context,self.game_logic.actual_level))
        #     if xinput_status['Y']:
        #         self.window.on_close()