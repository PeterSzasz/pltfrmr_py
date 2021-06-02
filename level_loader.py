from arcade import tilemap, SpriteList, color, check_for_collision_with_list
from pyglet.gl import GL_LINEAR
from actors import Enemy

class MapLoader():
    """
    Loads a .tmx file.
    Layers: walls, ladders, boxes, background
    """

    def __init__(self, tmx_file) -> None:
        self.SCALE = 4.0
        lvl = tilemap.read_tmx(tmx_file)
        self.background_list = tilemap.process_layer(lvl,
                                                "background",
                                                self.SCALE,
                                                use_spatial_hash=True)    # turn false when pymunk
        self.walls_list = tilemap.process_layer(lvl,
                                                "walls",
                                                self.SCALE,
                                                use_spatial_hash=True)    # turn false when pymunk
        self.ladders_list = tilemap.process_layer(lvl,
                                                "ladders",
                                                self.SCALE,
                                                use_spatial_hash=True)    # turn false when pymunk
        self.boxes_list = tilemap.process_layer(lvl,
                                                "boxes",
                                                self.SCALE)
        self.platforms_list = tilemap.process_layer(lvl,
                                                "moving_platforms",
                                                self.SCALE)
        for platform in self.platforms_list:
            self.walls_list.append(platform)
        self.background_color = color.AERO_BLUE
        self.MAP_GRAVITY = 1.0
        self.enemies_list = SpriteList()
        self.full_size_width = (lvl.map_size.width - 1) * \
            lvl.tile_size.width * \
            self.SCALE

        # test enemy
        self.enemy_no1 = Enemy(1500, 256)
        self.enemies_list.append(self.enemy_no1)

    def on_update(self, delta_time=1/60):
        self.enemies_list.on_update(delta_time)
        for enemy in self.enemies_list:
            enemy.center_x += enemy.change_x
            walls_hit = check_for_collision_with_list(enemy, self.walls_list)
            if walls_hit:
                enemy.change_x *= -1


    def draw(self) -> None:
        self.background_list.draw(filter=GL_LINEAR)
        self.walls_list.draw(filter=GL_LINEAR)
        self.ladders_list.draw(filter=GL_LINEAR)
        self.boxes_list.draw(filter=GL_LINEAR)
        self.enemies_list.draw(filter=GL_LINEAR)
