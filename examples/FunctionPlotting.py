from manim import *
import numpy as np

class FunctionPlotting(Scene):
    def construct(self):
        # Create axes
        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[-3, 3, 1],
            axis_config={"color": GREY_A},
            tips=False,
        )
        
        # Define and plot functions
        quadratic = axes.plot(lambda x: x**2, color=BLUE_C)
        sine = axes.plot(lambda x: np.sin(x), color=GREEN_C)
        
        # Add labels
        quadratic_label = axes.get_graph_label(quadratic, label='x^2', x_val=-2)
        sine_label = axes.get_graph_label(sine, label='\\sin(x)', x_val=1.5)
        
        # Animate
        self.play(Create(axes))
        self.play(Create(quadratic), Write(quadratic_label))
        self.wait(1)
        self.play(FadeOut(quadratic), FadeOut(quadratic_label))
        self.play(Create(sine), Write(sine_label))
        self.wait(2)
