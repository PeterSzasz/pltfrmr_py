# effects, shaders, etc

from attr import dataclass
from time import time
from math import sin,cos
from array import array
from random import uniform
from arcade import gl, get_window


@dataclass
class Burst:
    """ Track for each burst. """
    buffer: gl.Buffer
    vao: gl.Geometry
    start_time: float


class JetBurst:
    def __init__(self) -> None:
        ''''''
        self.burst_list = []
        self.offset_x = 0.0
        self.offset_y = 0.0
        # Program to visualize the points
        window = get_window()
        self.program = window.ctx.load_program(
            vertex_shader="assets/shaders/vertex_shader_jetpack.glsl",
            fragment_shader="assets/shaders/fragment_shader_jetpack.glsl",
        )
        #window.ctx.enable_only()

    def set_offset(self, x, y):
        self.offset_x = x
        self.offset_y = y

    def jet_burst(self, x, y):
        window = get_window()
        def _gen_initial_data(initial_x, initial_y):
            """ Generate data for each particle """
            for _ in range(100):
                # dx = uniform(-.1, .1)
                # dy = uniform(-.2, 0.0)
                base_angle = 1.0 * 3.1415
                beta = 0.075 * 3.1415    # 15deg
                angle = uniform(base_angle-beta, base_angle+beta)
                speed = uniform(0.0, 0.3)
                dx = sin(angle) * speed
                dy = cos(angle) * speed
                yield initial_x
                yield initial_y
                yield dx
                yield dy

        # Recalculate the coordinates from pixels to the OpenGL system with
        # 0, 0 at the center.
        x2 = self.offset_x + x / window.width * 2. - 1.
        y2 = self.offset_y + y / window.height * 2. - 1.

        # Get initial particle data
        initial_data = _gen_initial_data(x2, y2)

        # Create a buffer with that data
        buffer = window.ctx.buffer(data=array('f', initial_data))

        # Create a buffer description that says how the buffer data is formatted.
        buffer_description = gl.BufferDescription(  buffer,
                                                    '2f 2f',
                                                    ['in_pos', 'in_vel'])
        # Create our Vertex Attribute Object
        vao = window.ctx.geometry([buffer_description])

        # Create the Burst object and add it to the list of bursts
        burst = Burst(buffer=buffer, vao=vao, start_time=time())
        self.burst_list.append(burst)

    def on_draw(self):
        window = get_window()
        # Set the particle size
        window.ctx.point_size = 2 * window.get_pixel_ratio()

        # Loop through each burst
        for burst in self.burst_list:

            # Set the uniform data
            self.program['time'] = time() - burst.start_time

            # Render the burst
            burst.vao.render(self.program, mode=window.ctx.POINTS)