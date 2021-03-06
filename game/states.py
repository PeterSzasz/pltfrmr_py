# views for menu, game, scores, etc

import arcade
import arcade.gui
from arcade.arcade_types import Point
from arcade import View
from pyglet.gl import GL_LINEAR, GL_NEAREST
from pyglet.event import EventDispatcher
from actors import EasyEnemies, MediumEnemies, HardEnemies
from level_loader import MapLoader
from game.logger import MovementLogger
from game.replay import LogReplay

class BaseState(View):
    def __init__(self, context=None):
        """
        Sets basic properties for different views.
        If context is given the properties are already set here. Useful for first initialization.
        If context left out setup method needs to be called with it instead.
        """
        if context:
            super().__init__(context.window)
            self.game_logic = context.game_logic
            self.player = context.player
            self.input = context.game_logic.input
            self.context = context
        else:
            super().__init__()
            self.game_logic = None
            self.player = None
            self.input = None
            self.context = None
        arcade.set_background_color(arcade.color.LIGHT_MOSS_GREEN)
        self.bkg_image = arcade.load_texture("assets/backgrounds/bkg_4-rock.png")
        arcade.set_viewport(0.0, self.window.width, 0.0, self.window.height)

    def setup(self, context):
        """
        A place for setting up dynamic stuff. After initialization.
        The window attribute is handled by View's __init__ method.
        """
        self.game_logic = context.game_logic
        self.player = context.player
        self.input = context.game_logic.input
        self.context = context

    def set_next_state(self, state: 'BaseState'):
        state.setup(self.context)
        self.window.show_view(state)
        

class MainMenu(BaseState):
    """
    Manages the menu.
    """
    def __init__(self):
        super().__init__()
        self.menu_start = arcade.gui.UIFlatButton(text="ST.RT", width=200)
        self.menu_conf = arcade.gui.UIFlatButton(text="CONF", width=200)
        self.menu_info = arcade.gui.UIFlatButton(text="INFo", width=200)
        self.menu_quit = arcade.gui.UIFlatButton(text="q.UIT", width=200)
        self.v_box = arcade.gui.UIBoxLayout()
        self.gui_manager = arcade.gui.UIManager()

    def setup(self, context):
        '''Sets the player icon and finishes gui elements of the main menu.'''
        super().setup(context)

        player_right = self.player.walk_textures[0][0]
        player_left = self.player.walk_textures[1][0]
        player_back = self.player.climbing_textures[0][0]
        player_icon = arcade.gui.UITextureButton(100,100,50,50,player_right, player_left, player_back)

        self.v_box.add(player_icon)
        self.v_box.add(self.menu_start.with_space_around(bottom=30))
        self.v_box.add(self.menu_conf.with_space_around(bottom=30))
        self.v_box.add(self.menu_info.with_space_around(bottom=30))
        self.v_box.add(self.menu_quit)

        self.menu_start.on_click = self.on_click_start
        self.menu_conf.on_click = self.on_click_conf
        self.menu_info.on_click = self.on_click_info
        self.menu_quit.on_click = self.on_click_quit

        self.gui_manager.enable()
        self.gui_manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box
            )
        )

    def on_click_start(self, event):
        self.set_next_state(Gameplay(self.game_logic.actual_level))

    def on_click_conf(self, event):
        self.set_next_state(Conf())

    def on_click_info(self, event):
        self.set_next_state(Info(cat='rules'))

    def on_click_quit(self, event):
        self.window.on_close()

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
            self.set_next_state(Gameplay(self.game_logic.actual_level))
        if symbol == arcade.key.ESCAPE:
            self.window.on_close()
        self.input.on_key_press(symbol,modifiers)

    def on_update(self, delta_time: float):
        self.input.update()


class Gameplay(BaseState, EventDispatcher):
    """
    Manages the main gameplay area, handles input, renders everything.
    """
    def __init__(self, level_no: int = 1):
        super().__init__()
        self.level_no = level_no
        # Viewport settings
        self.LEFT_VIEW_MARGIN = 200
        self.RIGHT_VIEW_MARGIN = 300
        self.BOTTOM_VIEW_MARGIN = 50
        self.TOP_VIEW_MARGIN = 50
        self.viewport_left = 0
        self.viewport_bottom = 0
        # Texts
        self.static_text = "Alderaan VI"
        self.dinamy_text = "Score: "
        self.boxes_found = 0
        # Boxes
        self.BOXES = 5
        self.won_level = False
        # Gravity
        self.GRAVITY = 1500
        # Damping - Amount of speed lost per second
        self.DEFAULT_DAMPING = 1.0
        # Friction between objects
        self.WALL_FRICTION = 0.7
        self.DYNAMIC_ITEM_FRICTION = 0.6

    def setup(self, context) -> None:
        '''Initializes a level.'''
        super().setup(context)

        # Set up the empty sprite lists
        self.all_sprites = arcade.SpriteList()
        
        # set player
        self.player.reset_player(self.GRAVITY)
        from game.effects import JetBurst
        self.jet_burst = JetBurst()
        self.player.set_burst_effect(self.jet_burst)
        self.player.setup_subject(self.game_logic.input)
        self.all_sprites.append(self.player)

        # add logger and replayer
        self.movement_logger = MovementLogger(self)
        self.movement_logger.logging = False
        self.replayer = LogReplay(self.movement_logger)

        # map
        self.lvl = MapLoader(f"assets/maps/map_{self.level_no}.json")
        # test enemy
        if self.game_logic.difficulty == 1:
            enemies = EasyEnemies().get_enemy((500,500),self.game_logic.debug)
        if self.game_logic.difficulty == 2:
            enemies = MediumEnemies().get_enemy((500,500),self.game_logic.debug)
        if self.game_logic.difficulty == 3:
            enemies = HardEnemies().get_enemy((500,500),self.game_logic.debug)
        self.lvl.enemies_list.extend(enemies)
 
        # Create the physics engine
        # Default value is 1.0 if not specified.
        damping = self.DEFAULT_DAMPING
        # Set the gravity. (0, 0) is good for outer space and top-down.
        gravity = (0, -self.GRAVITY)
        self.physics_engine = arcade.PymunkPhysicsEngine(damping=damping,
                                                         gravity=gravity)
        self.physics_engine.add_sprite(self.player,
                                        friction=self.player.FRICTION,
                                        mass=self.player.MASS,
                                        moment_of_intertia=arcade.PymunkPhysicsEngine.MOMENT_INF,
                                        damping=self.player.DAMPING,
                                        collision_type="player",
                                        max_horizontal_velocity=self.player.MAX_H_SPEED,
                                        max_vertical_velocity=self.player.MAX_V_SPEED)
        self.physics_engine.add_sprite_list(self.lvl.scene.get_sprite_list("walls"),
                                            friction=self.WALL_FRICTION,
                                            collision_type="wall",
                                            body_type=arcade.PymunkPhysicsEngine.STATIC)
        self.physics_engine.add_sprite_list(self.lvl.scene.get_sprite_list("boxes"),
                                            mass=1,
                                            friction=self.DYNAMIC_ITEM_FRICTION,
                                            collision_type="box")
        if "moving_platforms" in self.lvl.scene.name_mapping:
            self.physics_engine.add_sprite_list(self.lvl.scene.get_sprite_list("moving_platforms"),
                                                body_type=arcade.PymunkPhysicsEngine.KINEMATIC)
        self.dispatch_event('start_level')

    def on_draw(self) -> None:
        '''iterates through everything that needs to appear for this level'''
        arcade.start_render()
        # texts
        arcade.draw_text(self.static_text, 26, 190, arcade.color.LIGHT_BROWN, 48)
        text = self.dinamy_text + str(self.boxes_found) + " <" + str(self.BOXES) + ">"
        arcade.draw_text(text, 4 + self.viewport_left, self.window.height-34, arcade.color.LIGHT_BROWN, 24)
        # draw a sun
        arcade.draw_circle_filled(900, 1100, 35, arcade.color.YELLOW_ORANGE)
        # draw the map
        self.lvl.draw(self.game_logic.debug)
        # draw effects
        self.jet_burst.on_draw()
        # draw player
        self.all_sprites.draw(filter=GL_NEAREST)
        
    def on_update(self, delta_time: float = 1/60) -> None:
        '''handles physics and game logic updates, win conditions, etc'''
        self.all_sprites.on_update(delta_time)
        self.lvl.on_update(delta_time)
        
        # update effects viewport offset
        self.jet_burst.set_offset(self.viewport_left, 0.0)
        
        # replay move, if replay started explicitly
        self.replayer.next_move()

        # controller handling
        self.input.update()

        # apply forces on player and calculate the physical aspect of the game
        self.player.on_ground = self.physics_engine.is_on_ground(self.player)
        self.physics_engine.apply_force(self.player, self.player.force)
        self.physics_engine.set_friction(self.player, self.player.FRICTION)
        self.physics_engine.apply_impulse(self.player, self.player.impulse)
        self.player.impulse = (0.0,0.0)
        self.physics_engine.step()

        # move platforms
        if "moving_platforms" in self.lvl.scene.name_mapping:
            platform_list = self.lvl.scene.get_sprite_list("moving_platforms")
        else:
            platform_list = []
        for platform in platform_list:
            if  (platform.boundary_right \
                and platform.change_x > 0 \
                and platform.right > platform.boundary_right) \
                or \
                (platform.boundary_left \
                and platform.change_x < 0 \
                and platform.left < platform.boundary_left):
                platform.change_x *= -1
            if  (platform.boundary_top \
                and platform.change_y > 0 \
                and platform.top > platform.boundary_top) \
                or \
                (platform.boundary_bottom \
                and platform.change_y < 0 \
                and platform.bottom < platform.boundary_bottom):
                platform.change_y *= -1

            # Figure out and set our moving platform velocity.
            # Pymunk uses velocity in pixels per second. If we instead have
            # pixels per frame, we need to convert.
            velocity = (platform.change_x * 1 / delta_time, platform.change_y * 1 / delta_time)
            self.physics_engine.set_velocity(platform, velocity)

        # check if we win
        if (self.lvl.full_size_width - 120) < self.player.center_x and self.window:
            self.dispatch_event('end_level')
            if self.game_logic.is_next_level():
                self.set_next_state(Gameplay(self.game_logic.next_level()))
            else:
                self.set_next_state(Info(cat='scores'))
            self.won_level = True

        # collision 
        # with boxes
        # colliding_boxes = arcade.check_for_collision_with_list(self.player, self.lvl.scene.get_sprite_list("boxes"))
        # for boxes in colliding_boxes:
        #     boxes.remove_from_sprite_lists()
        #     self.boxes_found += 1
        # with ladders
        if arcade.check_for_collision_with_list(self.player, self.lvl.scene.get_sprite_list("ladders")):
            if not self.player.on_ladder:
                self.player.on_ladder = True
        else:
            if self.player.on_ladder:
                self.player.on_ladder = False
        # with enemies
        colliding_enemies = arcade.check_for_collision_with_list(self.player, self.lvl.enemies_list)
        for enemy in colliding_enemies:
            enemy.health -= 4
            enemy.center_x = enemy.center_x-50
            if enemy.health < 0:
                enemy.remove_from_sprite_lists()

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
            self.dispatch_event('end_level')
            self.set_next_state(MainMenu())
        
        if symbol == arcade.key.R:
            self.movement_logger.logging = False
            self.movement_logger.setup_subject(self.replayer)
            self.replayer.set_observer(self.player)
            self.replayer.start_play(filename="movement.json")

        if symbol == arcade.key.P:
            #self.player.stop()  #TODO:replace this w something sensible
            self.set_next_state(Paused(self))

        if symbol == arcade.key.PRINT:
            image = arcade.get_image()
            image.save("screenshot.png", "PNG")

        self.input.on_key_press(symbol,modifiers)

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        self.input.on_key_release(symbol,modifiers)

Gameplay.register_event_type('start_level')
Gameplay.register_event_type('end_level')


class UIColoredLabel(arcade.gui.UILabel):
    def __init__(self, x: float = 0, y: float = 0, width: float = None, height: float = None, text: str = "", font_name=('Arial',), font_size: float = 12, text_color: arcade.Color=(255, 255, 255, 255), bold=False, bg_color=None, **kwargs):
        super().__init__(x=x, y=y, width=width, height=height, text=text, font_name=font_name, font_size=font_size, text_color=text_color, bold=bold, **kwargs)
        self.bg_color = bg_color
        if not self.bg_color:
            self.bg_color = (255,255,255,128)
    
    def do_render(self, surface):
        super().do_render(surface)
        arcade.draw_xywh_rectangle_filled(0, 0, self.width, self.height, color=self.bg_color)

class Conf(BaseState):
    """
    Manages the configuration screen.
    """
    def __init__(self):
        super().__init__()

    def setup(self, context):
        '''Sets options labels and buttons based on game_logic's data.'''
        super().setup(context)

        label_col = arcade.gui.UIBoxLayout(0,0,vertical=True, align="bottom")
        buttn_col = arcade.gui.UIBoxLayout(0,0,vertical=True)
        options = self.game_logic.options
        for key,value in options.items():
            label_col.add(UIColoredLabel(x=0.0,y=40.0,width=100,height=50,font_size=20,
                                         text=key,text_color=(155,44,155,255),bold=True,
                                         font_name="Kenney Pixel",bg_color=(11,11,11,111)))
            buttn_col.add(arcade.gui.UIFlatButton(x=0.0,y=0.0,width=100,height=50,
                                                  text=value[0]))
                        
        box_layout = arcade.gui.UIBoxLayout(x=self.window.width/2-100,
                                            y=self.window.height/2+200,
                                            vertical=False,
                                            children=[label_col,buttn_col])

        back_button = arcade.gui.UIFlatButton(self.window.width-150,80,text='Back')
        back_button.on_click = self.on_click_back
        self.gui_manager = arcade.gui.UIManager()
        self.gui_manager.enable()
        self.gui_manager.add(box_layout)
        self.gui_manager.add(back_button)

    def on_click_back(self, event):
        self.set_next_state(MainMenu())

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
            self.set_next_state(MainMenu())


class Info(BaseState):
    """
    Manages the info screen.
    """
    def __init__(self, cat=None):
        super().__init__()
        self.cat = cat

    def setup(self, context):
        '''Sets text based on category input and other gui elements.'''
        super().setup(context)

        if self.cat == 'rules':
            info_str =  "Collect boxes and reach the end of the map.\n" + \
                        "Move with [???,???] and jump with [space].\n" + \
                        "Climb with [???,???] if you must."
        elif self.cat == 'scores':
            info_str = f"Score: {self.game_logic.actual_level + self.game_logic.lives_left}"
        else:
            info_str = "No information about this. google it."

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
        self.set_next_state(MainMenu())

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
            self.set_next_state(MainMenu())


class Paused(BaseState):
    """
    Class to show a semi transparent pause screen during game.
    """
    def __init__(self, game_view: Gameplay):
        super().__init__()
        # reference to the game's level view
        self.game_view = game_view

    def setup(self, context):
        '''Sets the correct viewport, text and other gui elements.'''
        super().setup(context)

        arcade.set_viewport(self.game_view.viewport_left, 
                                self.window.width + self.game_view.viewport_left,
                                self.game_view.viewport_bottom, 
                                self.window.height + self.game_view.viewport_bottom)
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
            self.window.show_view(self.game_view)   # TODO: replace this when Paused is not a View anymore

        if symbol == arcade.key.ESCAPE:
            arcade.set_viewport(0.0, self.window.width, 0.0, self.window.height)  # else the next view is shifted too, should find a better fix
            self.set_next_state(MainMenu())