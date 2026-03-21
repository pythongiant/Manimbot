from manim import *
import numpy as np

class ThreeDVisualization(Scene):
    def construct(self):
        axes = ThreeDAxes()
        
        # Create a parametric curve in 3D
        def param_curve(t):
            return np.array([
                2 * np.sin(t),
                2 * np.cos(t),
                t / 2
            ])
        
        curve = ParametricFunction(
            param_curve,
            t_range=[0, 4*PI],
            color=BLUE
        )
        
        # Create surface
        surface = Surface(
            lambda u, v: np.array([
                np.sin(u) * np.cos(v),
                np.sin(u) * np.sin(v),
                np.cos(u)
            ]),
            u_range=[0, PI],
            v_range=[0, 2*PI],
            color=PURPLE,
            opacity=0.7
        )
        
        self.add(axes)
        self.add(surface)
        self.play(Create(curve), run_time=3)
        self.move_camera(phi=75*DEGREES, theta=45*DEGREES)
        self.wait(2)
