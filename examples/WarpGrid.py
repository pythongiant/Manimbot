from manim import *
import numpy as np

class WarpGrid(Scene):
    def construct(self):
        grid = NumberPlane()
        self.add(grid)

        grid.prepare_for_nonlinear_transform()
        self.play(
            grid.animate.apply_function(
                lambda p: p + np.array([
                    np.sin(p[1]),
                    np.sin(p[0]),
                    0
                ])
            ),
            run_time=3
        )
        self.wait()
