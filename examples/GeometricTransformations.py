from manim import *

class GeometricTransformations(Scene):
    def construct(self):
        # Create a grid of shapes
        shapes = VGroup()
        for i in range(4):
            for j in range(4):
                shape = Circle(radius=0.2, color=BLUE)
                shape.shift(RIGHT * (i - 1.5) + UP * (j - 1.5))
                shapes.add(shape)
        
        self.add(shapes)
        
        # Apply various transformations
        self.play(shapes.animate.scale(1.5), run_time=1)
        self.play(shapes.animate.rotate(PI/4), run_time=1)
        self.play(shapes.animate.shift(RIGHT * 2), run_time=1)
        self.play(ApplyWave(shapes, time_width=0.5), run_time=2)
        self.play(Restore(shapes), run_time=1)
