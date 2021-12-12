from arcade import tilemap, SpriteList, color, check_for_collision_with_list
from arcade import Scene
from pyglet.gl import GL_LINEAR, GL_NEAREST
from actors import Enemy

class MapLoader():
    """
    Loads a .json file.
    Layers: walls, ladders, boxes, background tiles, etc
    """

    def __init__(self, map_file) -> None:
        SCALE = 4.0
        self.MAP_GRAVITY = 1.0
        self.background_color = color.AERO_BLUE

        layer_options = {
            "background": {
                "use_spatial_hash": True
            },
            "walls": {
                "use_spatial_hash": True
            },
            "ladders": {
                "use_spatial_hash": True
            },
            "boxes": {
                "use_spatial_hash": False
            },
            "moving_platforms": {
                "use_spatial_hash": False
            }
        }   # other layers: boxes, moving_platforms

        self.tile_map = tilemap.tilemap.load_tilemap(map_file, SCALE, layer_options)
        self.scene = Scene.from_tilemap(self.tile_map)

        self.full_size_width = (self.tile_map.width - 1) * \
            self.tile_map.tile_width * \
            SCALE
        
        # test enemy
        self.enemies_list = SpriteList()
        self.enemy_no1 = Enemy(1500, 256)
        self.enemies_list.append(self.enemy_no1)

    def on_update(self, delta_time=1/60):
        self.enemies_list.on_update(delta_time)
        for enemy in self.enemies_list:
            enemy.center_x += enemy.change_x
            walls_hit = check_for_collision_with_list(enemy, self.scene.get_sprite_list("walls"))
            if walls_hit:
                enemy.change_x *= -1


    def draw(self) -> None:
        self.scene.draw(filter=GL_NEAREST)
        self.enemies_list.draw(filter=GL_NEAREST)
