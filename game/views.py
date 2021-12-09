# views for menu, game, scores, etc

import arcade
import arcade.gui
from arcade.arcade_types import Point
from arcade import View
from pyglet.gl import GL_LINEAR, GL_NEAREST
from pyglet.event import EventDispatcher
from level_loader import MapLoader
from game.replay import LogReplay

class MenuView(View):
    """
    Manages the menu.
    """
    def __init__(self, window):
        super().__init__(window)
        
        arcade.set_background_color(arcade.color.LIGHT_MOSS_GREEN)
        self.bkg_image = arcade.load_texture("assets/backgrounds/bkg_4-rock.png")

        menu_start = arcade.gui.UIFlatButton(text="ST.RT", width=200)
        menu_info = arcade.gui.UIFlatButton(text="INFO", width=200)
        menu_quit = arcade.gui.UIFlatButton(text="qUIT", width=200)

        self.v_box = arcade.gui.UIBoxLayout()
        self.v_box.add(menu_start.with_space_around(bottom=30))
        self.v_box.add(menu_info.with_space_around(bottom=30))
        self.v_box.add(menu_quit)

        menu_start.on_click = self.on_click_start
        menu_info.on_click = self.on_click_info
        menu_quit.on_click = self.on_click_quit

        self.gui_manager = arcade.gui.UIManager()
        self.gui_manager.enable()
        self.gui_manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box
            )
        )

    def on_click_info(self, event):
        print('info clicked')
        self.window.show_view(InfoView(self.window))

    def on_click_quit(self, event):
        print('quit clicked')
        #self.window.show_view(QuitPopup)
        self.window.on_close()

    def on_click_start(self, event):
        print('start clicked')
        self.window.show_view(LevelView(self.window, level_no=1))

    def on_draw(self):
        arcade.start_render()
        arcade.draw_texture_rectangle(
            self.window.width/2,
            self.window.height/2,
            self.window.width,
            self.window.height,
            self.bkg_image
        )
        self.gui_manager.draw()

    def on_key_press(self, symbol: int, modifiers: int):
        super().on_key_press(symbol, modifiers)
        if symbol == arcade.key.ENTER:
            print('start hit')
            self.window.show_view(LevelView(self.window, level_no=1))
        if symbol == arcade.key.ESCAPE:
            print('exiting menu')
            self.window.on_close()


class LevelView(View, EventDispatcher):
    """
    Manages the main gameplay area.
    """
    def __init__(self, window, level_no: int = 1):
        super().__init__(window)
        self.initial_setup(level_no)

    def initial_setup(self, level_no: int = 1) -> None:
        """Initializes a level. Handles keyb input. Renders."""

        # set background color
        arcade.set_background_color(arcade.color.LIGHT_MOSS_GREEN)

        # viewport settings
        self.LEFT_VIEW_MARGIN = 200
        self.RIGHT_VIEW_MARGIN = 300
        self.BOTTOM_VIEW_MARGIN = 50
        self.TOP_VIEW_MARGIN = 50
        self.viewport_left = 0
        self.viewport_bottom = 0

        # Set up the empty sprite lists
        self.all_sprites = arcade.SpriteList()
        
        # texts
        self.static_text = "Alderaan VI"
        self.dinamy_text = "Score: "
        self.boxes_found = 0

        # add player
        self.player = self.window.player
        self.player.reset_player()
        self.player.setup_subject(self)
        self.all_sprites.append(self.player)

        # add logger and replayer
        self.window.movement_logger.setup_subject(self)
        self.window.movement_logger.logging = True
        self.replayer = LogReplay(self.window.movement_logger)

        # map
        self.lvl = MapLoader(f"assets/maps/map_{level_no}.json")
 
        # no. of boxes
        self.BOXES = 5
        self.won_level = False

        # turn on physics engine
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player, 
                                                            self.lvl.scene.get_sprite_list("walls"), 
                                                            self.lvl.MAP_GRAVITY, 
                                                            self.lvl.scene.get_sprite_list("ladders"))
        self.dispatch_event('start_level')

    def on_draw(self) -> None:
        arcade.start_render()
        # texts
        arcade.draw_text(self.static_text, 16, 190, arcade.color.LIGHT_BROWN, 48)
        text = self.dinamy_text + str(self.boxes_found) + " <" + str(self.BOXES) + ">"
        arcade.draw_text(text, 4 + self.viewport_left, self.window.height-34, arcade.color.LIGHT_BROWN, 24)
        # draw a sun
        arcade.draw_circle_filled(900, 1100, 35, arcade.color.YELLOW_ORANGE)
        # draw the map
        self.lvl.draw()
        # draw player
        self.all_sprites.draw(filter=GL_NEAREST)
        
    def on_update(self, delta_time: float = 1/60) -> None:
        self.all_sprites.on_update(delta_time)
        self.lvl.on_update(delta_time)
        self.physics_engine.update()
        
        self.replayer.next_move()

        # check if we win
        if (self.lvl.full_size_width - 120) < self.player.center_x and self.window:
                # else the next view is shifted too, should find a better fix
                arcade.set_viewport(0.0, self.window.width, 0.0, self.window.height)
                #gstate.on_event("start_next_level")
                self.dispatch_event('end_level')
                self.window.show_view(LevelView(self.window,self.window.logic.next_level()))
                self.won_level = True

        # check for collision
        colliding_boxes = arcade.check_for_collision_with_list(self.player, self.lvl.scene.get_sprite_list("boxes"))
        for boxes in colliding_boxes:
            boxes.remove_from_sprite_lists()
            self.boxes_found += 1

        # check for enemy collision
        colliding_enemies = arcade.check_for_collision_with_list(self.player, self.lvl.enemies_list)
        for enemy in colliding_enemies:
            enemy.remove_from_sprite_lists()
            print("Gotcha!")

        # viewport scrolling
        changed = False
        if self.player.left < self.viewport_left + self.LEFT_VIEW_MARGIN:
            self.viewport_left -= self.viewport_left + self.LEFT_VIEW_MARGIN - self.player.left
            if self.viewport_left < 0:
                self.viewport_left = 0
            changed = True

        viewport_right = self.viewport_left + self.window.width
        if self.player.right > viewport_right - self.RIGHT_VIEW_MARGIN:
            self.viewport_left += self.player.right - (viewport_right - self.RIGHT_VIEW_MARGIN)
            changed = True

        if changed and not self.won_level:
            self.viewport_left = int(self.viewport_left)
            self.viewport_bottom = int(self.viewport_bottom)
            arcade.set_viewport(self.viewport_left, 
                                self.window.width + self.viewport_left,
                                self.viewport_bottom, 
                                self.window.height + self.viewport_bottom)

    def on_key_press(self, symbol: int, modifiers: int) -> None:

        if symbol == arcade.key.ESCAPE:
            # else the next view is shifted too, should find a better fix
            self.dispatch_event('end_level')
            arcade.set_viewport(0.0, self.window.width, 0.0, self.window.height)
            self.window.show_view(MenuView(self.window))   #("back_to_menu")
        
        if symbol == arcade.key.R:
            self.window.movement_logger.logging = False
            self.window.movement_logger.setup_subject(self.replayer)
            self.replayer.set_observer(self.player)
            self.replayer.start_play()

        if symbol == arcade.key.P:
            # pause the game
            self.player.stop()  #TODO:replace this w something
            self.window.show_view(PauseView(self.window, game_view=self))

        if symbol == arcade.key.SPACE:
            if self.physics_engine.can_jump():
                self.dispatch_event('jump')
            else:
                self.dispatch_event('move_up',True)

        if symbol == arcade.key.UP:
            self.dispatch_event('move_up',True)

        if symbol == arcade.key.DOWN:
            self.dispatch_event('move_down',True)

        if symbol == arcade.key.LEFT:
            self.dispatch_event('move_left',True)
            # TODO: do not allow moving through left map boundary

        if symbol == arcade.key.RIGHT:
            self.dispatch_event('move_right',True)
            # TODO: do not allow moving through right map boundary

        if symbol == arcade.key.PRINT:
            image = arcade.get_image()
            image.save("screenshot.png", "PNG")

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        if symbol == arcade.key.UP:
            self.dispatch_event('move_up',False)

        if symbol == arcade.key.DOWN:
            self.dispatch_event('move_down',False)

        if symbol == arcade.key.LEFT:
            self.dispatch_event('move_left',False)

        if symbol == arcade.key.RIGHT:
            self.dispatch_event('move_right',False)

LevelView.register_event_type('move_right')
LevelView.register_event_type('move_left')
LevelView.register_event_type('move_up')
LevelView.register_event_type('move_down')
LevelView.register_event_type('jump')
LevelView.register_event_type('start_level')
LevelView.register_event_type('end_level')

class InfoView(View):
    """
    Manages the info screen.
    """
    def __init__(self, window, info_str=None):
        super().__init__(window)
        self.bkg_image = arcade.load_texture("assets/backgrounds/bkg_4-rock.png")
        if info_str is None:
            info_str = "Collect boxes and reach the end of the map.\n" + \
                            "Move with [←,→] and jump with [space].\n" + \
                            "Climb with [↑,↓] if you must."
        info = arcade.gui.UITextArea(self.window.width/2-500,   # TODO: should change to UILabel or something with more options
                                    self.window.height/2-250,
                                    width=800,
                                    height=500,
                                    text=info_str,
                                    font_size=40,
                                    bold=True,
                                    color=arcade.color.RED)
        back_button = arcade.gui.UIFlatButton(self.window.width-150,80,text='Back')
        back_button.on_click = self.on_click_back
        self.gui_manager = arcade.gui.UIManager()
        self.gui_manager.enable()
        self.gui_manager.add(info)
        self.gui_manager.add(back_button)

    def on_click_back(self, event):
        print('back clicked')
        self.window.show_view(MenuView(self.window))

    def on_draw(self):
        arcade.start_render()
        arcade.draw_texture_rectangle(
            self.window.width/2,
            self.window.height/2,
            self.window.width,
            self.window.height,
            self.bkg_image
        )
        self.gui_manager.draw()

    def on_key_press(self, symbol: int, modifiers: int):
        super().on_key_press(symbol, modifiers)
        if symbol == arcade.key.ENTER or symbol == arcade.key.ESCAPE:
            print('enter/esc hit')
            self.window.show_view(MenuView(self.window))


class ScoreboardView(View):
    """
    Manages the Score view.
    """
    def __init__(self, window, info_str=None):
        super().__init__(window)
        self.bkg_image = arcade.load_texture("assets/backgrounds/bkg_4-rock.png")
        if info_str is None:
            info_str = f"Score: {self.window.logic.actual_level + self.window.logic.lives_left}"
        info = arcade.gui.UITextArea(self.window.width/2-100,   # TODO: should change to UILabel or something with more options
                                    self.window.height/2+50,
                                    width=400,
                                    height=500,
                                    text=info_str,
                                    font_size=40,
                                    bold=True,
                                    color=arcade.color.WHITE_SMOKE)        
        back_button = arcade.gui.UIFlatButton(self.width-150,80,text='BACK')
        back_button.on_click = self.on_click_back
        self.gui_manager = arcade.gui.UIManager()
        self.gui_manager.enable()
        self.gui_manager.add(info)
        self.gui_manager.add(back_button)

    def on_click_back(self, event):
        print('back clicked')
        self.window.show_view(MenuView(self.window))

    def on_draw(self):
        super().on_draw()
        arcade.start_render()
        arcade.draw_texture_rectangle(
            self.window.width/2,
            self.window.height/2,
            self.window.width,
            self.window.height,
            self.bkg_image
        )
        self.gui_manager.draw()

    def on_key_press(self, symbol: int, modifiers: int):
        super().on_key_press(symbol, modifiers)
        if symbol == arcade.key.ENTER or symbol == arcade.key.ESCAPE:
            print('enter/esc hit')
            self.window.show_view(MenuView(self.window))


class PauseView(View):
    """Class to shows a semi transparent pause screen during game."""

    def __init__(self, window, game_view: LevelView):
        super().__init__(window)
        # reference to the game's level view
        self.game_view = game_view
        # a semitransparent color for the overlay
        self.fill_color = arcade.make_transparent_color(
            arcade.color.WHITE, transparency=150
        )
        self.gui_manager = arcade.gui.UIManager()
        self.gui_manager.enable()
        text = "-=PAUSED=-\n\nP TO CONTINUE\nESC TO EXIT"
        info = arcade.gui.UITextArea(   self.game_view.viewport_left + self.window.width/2-200,   # TODO: should change to UILabel or something with more options
                                        self.game_view.viewport_bottom + self.window.height/2-100,
                                        width=400,
                                        height=500,
                                        text=text,
                                        font_size=40,
                                        bold=False,
                                        color=arcade.color.DARK_GREEN)
        self.gui_manager.add(info)

    def on_draw(self):
        # draw the paused game in the background
        self.game_view.on_draw()
        arcade.draw_lrtb_rectangle_filled(self.game_view.viewport_left,
                                        self.game_view.viewport_left + self.window.width,
                                        self.game_view.viewport_bottom + self.window.height,
                                        self.game_view.viewport_bottom,
                                        self.fill_color
        )
        self.gui_manager.draw()

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        # resume the game when the user presses ESC again
        if symbol == arcade.key.P:
            #self.window.show_view(self.game_view)
            self.window.show_view(self.game_view)

        if symbol == arcade.key.ESCAPE:
            arcade.set_viewport(0.0, self.window.width, 0.0, self.window.height)  # else the next view is shifted too, should find a better fix
            self.window.show_view(MenuView(self.window))