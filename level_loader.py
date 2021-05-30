from arcade import tilemap, SpriteList, color
from pyglet.gl import GL_LINEAR

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
                                                use_spatial_hash = True)    # turn false when pymunk
        self.walls_list = tilemap.process_layer(lvl,
                                                "walls",
                                                self.SCALE,
                                                use_spatial_hash = True)    # turn false when pymunk
        self.ladders_list = tilemap.process_layer(lvl,
                                                "ladders",
                                                self.SCALE,
                                                use_spatial_hash = True)    # turn false when pymunk
        self.boxes_list = tilemap.process_layer(lvl,
                                                "boxes",
                                                self.SCALE)
        
        self.background_color = color.AERO_BLUE
        self.MAP_GRAVITY = 1.0
        self.enemies_list = SpriteList()
        self.full_size_width = (lvl.map_size.width - 1) * \
            lvl.tile_size.width * \
            self.SCALE

    def draw(self) -> None:
        self.background_list.draw(filter = GL_LINEAR)
        self.walls_list.draw(filter = GL_LINEAR)
        self.ladders_list.draw(filter = GL_LINEAR)
        self.boxes_list.draw(filter = GL_LINEAR)
