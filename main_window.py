# main file of a platformer
# - simple
# - working menu system
# - using tmx files from tiled editor

import pymunk
from typing import Optional
import arcade
import arcade.gui
from arcade.arcade_types import Point
#from pyglet.gl import GL_NEAREST
from pyglet.gl import GL_LINEAR
import actors
from level_loader import MapLoader

class GameStateHandler():
    def __init__(self, width: int, height: int, window: arcade.Window) -> None:
        self.actual_level = 1
        self.max_level = 2
        self.lives_left = 3
        self.SCREEN_WIDTH = width
        self.SCREEN_HEIGHT = height
        self.window = window

    def on_event(self, name) -> None:
        '''
        handles incoming events;
        stores the returning new state as new actual state
        if event was valid
        '''

        if name == "back_to_menu" or name == "start_app":
            print("back to main menu")
            menu = MenuView(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
            self.window.show_view(menu)
        if name == "start_new_game":
            print("in Menu, start new game")
            self.actual_level = 1
            new_level = LevelView(self.SCREEN_WIDTH,
                                    self.SCREEN_HEIGHT,
                                    self.actual_level)
            self.window.show_view(new_level)
        if name == "start_next_level" or name == "continue":
            self.actual_level += 1
            if self.actual_level <= self.max_level:
                print(f"in game/menu, start {self.actual_level}. level")
                new_level = LevelView(self.SCREEN_WIDTH,
                                        self.SCREEN_HEIGHT,
                                        self.actual_level)
                self.window.show_view(new_level)
            else:
                print("game won")
                scores = ScoreboardView(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
                self.window.show_view(scores)
        if name == "show_info":
            print("showing info screen")
            infoview = InfoView(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
            self.window.show_view(infoview)
        if name == "quit_game":
            print("exiting game")
            self.window.on_close()


# game logic initialization
gstate = None


class MenuView(arcade.View):
    """
    Manages the menu.
    """

    def __init__(self, width, height):
        super().__init__()
        self.SCREEN_WIDTH = width
        self.SCREEN_HEIGHT = height        
        arcade.set_background_color(arcade.color.LIGHT_MOSS_GREEN)
        self.bkg_image = arcade.load_texture("assets/backgrounds/bkg_4-rock.png")

        self.gui_manager = arcade.gui.UIManager()
        self.gui_manager.enable()

        self.v_box = arcade.gui.UIBoxLayout()

        menu_start = arcade.gui.UIFlatButton(text="ST.RT", width=200)
        self.v_box.add(menu_start.with_space_around(bottom=30))
        @menu_start.event("on_click")
        def on_click_start(event):
            print('start clicked')
            gstate.on_event("start_new_game")

        menu_info = arcade.gui.UIFlatButton(text="INFO", width=200)
        self.v_box.add(menu_info.with_space_around(bottom=30))
        @menu_info.event("on_click")
        def on_click_info(event):
            print('info clicked')
            gstate.on_event("show_info")

        menu_quit = arcade.gui.UIFlatButton(text="qUIT", width=200)
        self.v_box.add(menu_quit)
        @menu_quit.event("on_click")
        def on_click_quit(event):
            print('quit clicked')
            gstate.on_event("quit_game")

        self.gui_manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box
            )
        )

    def on_draw(self):
        arcade.start_render()
        arcade.draw_texture_rectangle(
            self.SCREEN_WIDTH/2,
            self.SCREEN_HEIGHT/2,
            self.SCREEN_WIDTH,
            self.SCREEN_HEIGHT,
            self.bkg_image
        )
        self.gui_manager.draw()

    def on_key_press(self, symbol: int, modifiers: int):
        super().on_key_press(symbol, modifiers)
        if symbol == arcade.key.ENTER:
            print('start Entered')
            gstate.on_event("start_new_game")
        if symbol == arcade.key.ESCAPE:
            print('exiting menu')
            gstate.on_event("quit_game")


class InfoView(arcade.View):
    """
    Manages the info screen.
    """

    def __init__(self, width, height):
        super().__init__()
        self.SCREEN_WIDTH = width
        self.SCREEN_HEIGHT = height
        self.bkg_image = arcade.load_texture("assets/backgrounds/bkg_4-rock.png")
        self.info_str = "Collect boxes and reach the end of the map.\n" + \
                        "Move with [←,→] and jump with [space].\n" + \
                        "Climb with [↑,↓] if you must."

        self.gui_manager = arcade.gui.UIManager()
        self.gui_manager.enable()

        info = arcade.gui.UITextArea(self.SCREEN_WIDTH/2-500,   # TODO: should change to UILabel or something with more options
                                    self.SCREEN_HEIGHT/2-250,
                                    width=800,
                                    height=500,
                                    text=self.info_str,
                                    font_size=40,
                                    bold=True,
                                    color=arcade.color.WHITE_SMOKE)
        
        back_button = arcade.gui.UIFlatButton(self.SCREEN_WIDTH-150,
                                                    80,
                                                    text='Back')
        @back_button.event("on_click")
        def on_click_back(event):
            print('back clicked')
            gstate.on_event("back_to_menu")

        self.gui_manager.add(info)
        self.gui_manager.add(back_button)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_texture_rectangle(
            self.SCREEN_WIDTH/2,
            self.SCREEN_HEIGHT/2,
            self.SCREEN_WIDTH,
            self.SCREEN_HEIGHT,
            self.bkg_image
        )
        self.gui_manager.draw()

    #def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
    #    super().on_mouse_press(x, y, button, modifiers)
    #    if self.back.collides_with_point((x,y)) and gstate:


class ScoreboardView(arcade.View):
    def __init__(self, width, height):
        super().__init__()
        self.SCREEN_WIDTH = width
        self.SCREEN_HEIGHT = height
        self.bkg_image = arcade.load_texture("assets/backgrounds/bkg_4-rock.png")
        self.info = arcade.draw_text(f"Score: {gstate.actual_level + gstate.lives_left}",
                                        self.SCREEN_WIDTH/2-50,
                                        50,
                                        arcade.color.BLACK,
                                        font_size=40,
                                        bold=True,
                                        align="center")
        self.back = arcade.draw_text("BACK",
                                        self.SCREEN_WIDTH-150,
                                        50,
                                        arcade.color.BLACK,
                                        font_size=40,
                                        bold=True,
                                        align="center")

    def on_draw(self):
        super().on_draw()
        arcade.start_render()
        arcade.draw_texture_rectangle(
            self.SCREEN_WIDTH/2,
            self.SCREEN_HEIGHT/2,
            self.SCREEN_WIDTH,
            self.SCREEN_HEIGHT,
            self.bkg_image
        )
        self.info.draw()
        self.back.draw()

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        super().on_mouse_press(x, y, button, modifiers)
        if self.back.collides_with_point((x,y)) and gstate:
            gstate.on_event("back_to_menu")


class LevelView(arcade.View):
    """
    Manages the main gameplay area.
    """

    def __init__(self, width: int, height: int, level_no: int = 1) -> None:
        super().__init__()
        self.SCREEN_WIDTH = width
        self.SCREEN_HEIGHT = height
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
        self.player = actors.MainActor()
        self.all_sprites.append(self.player)

        # map
        self.lvl = MapLoader(f"assets/maps/map_{level_no}.tmx")
        print(level_no)
 
        # no. of boxes
        self.BOXES = 5
        self.won_level = False

        # turn on physics engine
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player, 
                                                            self.lvl.walls_list, 
                                                            self.lvl.MAP_GRAVITY, 
                                                            self.lvl.ladders_list)

    def on_draw(self) -> None:
        arcade.start_render()
        # texts
        arcade.draw_text(self.static_text, 16, 190, arcade.color.LIGHT_BROWN, 48)
        text = self.dinamy_text + str(self.boxes_found) + " <" + str(self.BOXES) + ">"
        arcade.draw_text(text, 4 + self.viewport_left, self.SCREEN_HEIGHT-34, arcade.color.LIGHT_BROWN, 24)
        # draw a sun
        arcade.draw_circle_filled(900, 1100, 35, arcade.color.YELLOW_ORANGE)
        # draw the map
        self.lvl.draw()
        # draw player
        self.all_sprites.draw(filter=GL_LINEAR)
        
    def on_update(self, delta_time: float = 1/60) -> None:
        self.all_sprites.on_update(delta_time)
        self.lvl.on_update(delta_time)
        self.physics_engine.update()
        
        # check if we win
        if (self.lvl.full_size_width - 120) < self.player.center_x:
            if gstate:
                # else the next view is shifted too, should find a better fix
                arcade.set_viewport(0.0, self.SCREEN_WIDTH, 0.0, self.SCREEN_HEIGHT)
                gstate.on_event("start_next_level")
                self.won_level = True

        # check for collision
        colliding_boxes = arcade.check_for_collision_with_list(self.player, self.lvl.boxes_list)
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

        viewport_right = self.viewport_left + self.SCREEN_WIDTH
        if self.player.right > viewport_right - self.RIGHT_VIEW_MARGIN:
            self.viewport_left += self.player.right - (viewport_right - self.RIGHT_VIEW_MARGIN)
            changed = True

        if changed and not self.won_level:
            self.viewport_left = int(self.viewport_left)
            self.viewport_bottom = int(self.viewport_bottom)
            arcade.set_viewport(self.viewport_left, 
                                self.SCREEN_WIDTH + self.viewport_left,
                                self.viewport_bottom, 
                                self.SCREEN_HEIGHT + self.viewport_bottom)

    def on_key_press(self, symbol: int, modifiers: int) -> None:

        if symbol == arcade.key.ESCAPE:
            # else the next view is shifted too, should find a better fix
            arcade.set_viewport(0.0, self.SCREEN_WIDTH, 0.0, self.SCREEN_HEIGHT)
            gstate.on_event("back_to_menu")
        
        if symbol == arcade.key.P:
            # pause the game
            pause = PauseView(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, game_view=self)
            self.window.show_view(pause)

        if symbol == arcade.key.SPACE:
            if self.physics_engine.can_jump():
                self.player.jump()
                #if self.player.player_jump_snd != None:
                #    arcade.play_sound(self.player.player_jump_snd)
            else:
                self.player.move_up(True)

        if symbol == arcade.key.UP:
            self.player.move_up(True)

        if symbol == arcade.key.DOWN:
            self.player.move_down(True)

        if symbol == arcade.key.LEFT:
            self.player.move_left(True)
            # TODO: do not allow moving through left map boundary

        if symbol == arcade.key.RIGHT:
            self.player.move_right(True)
            # TODO: do not allow moving through right map boundary

        if symbol == arcade.key.PRINT:
            image = arcade.get_image()
            image.save("screenshot.png", "PNG")

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        if symbol == arcade.key.UP:
            self.player.move_up(False)

        if symbol == arcade.key.DOWN:
            self.player.move_down(False)

        if symbol == arcade.key.LEFT:
            self.player.move_left(False)

        if symbol == arcade.key.RIGHT:
            self.player.move_right(False)


class PauseView(arcade.View):
    """Class to shows a semi transparent pause screen during game."""

    def __init__(self, width: int, height: int, game_view: arcade.View) -> None:
        super().__init__()
        self.SCREEN_WIDTH = width
        self.SCREEN_HEIGHT = height
        # reference to the underlying view
        self.game_view = game_view

        # a semitransparent color for the overlay
        self.fill_color = arcade.make_transparent_color(
            arcade.color.WHITE, transparency=150
        )

    def on_draw(self):
        # draw the paused game in the background
        self.game_view.on_draw()
        arcade.draw_lrtb_rectangle_filled(self.game_view.viewport_left,
                                        self.game_view.viewport_left + self.SCREEN_WIDTH,
                                        self.game_view.viewport_bottom + self.SCREEN_HEIGHT,
                                        self.game_view.viewport_bottom,
                                        self.fill_color
        )
        arcade.draw_text("-=PAUSED=-\n\nP TO CONTINUE\nESC TO EXIT",
                        self.game_view.viewport_left + self.SCREEN_WIDTH/2 - 200,
                        self.game_view.viewport_bottom + self.SCREEN_HEIGHT/2 - 100,
                        arcade.color.DARK_GREEN,
                        font_size=40,
                        align="center"
        )

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        # resume the game when the user presses ESC again
        if symbol == arcade.key.P:
            self.window.show_view(self.game_view)

        if symbol == arcade.key.ESCAPE:
            # else the next view is shifted too, should find a better fix
            arcade.set_viewport(0.0, self.SCREEN_WIDTH, 0.0, self.SCREEN_HEIGHT)
            gstate.on_event("back_to_menu")

        

if __name__ == "__main__":
    # app entry point
    TITLE = "Plfrmr 0.2"
    WIDTH = 1680
    HEIGHT = 1000
    window = arcade.Window(WIDTH, HEIGHT, TITLE)
    gstate = GameStateHandler(WIDTH, HEIGHT, window)
    gstate.on_event("start_app")
    arcade.run()