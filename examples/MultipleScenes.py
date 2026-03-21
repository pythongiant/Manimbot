from manim import *
import numpy as np


# ============================================================================
# Multiple Scenes in One File - Clean Examples
# ============================================================================


class CircleShrinking(Scene):
    """Scene that creates and shrinks a circle"""
    def construct(self):
        circle = Circle(color=BLUE, radius=2)
        self.play(Create(circle))
        self.play(circle.animate.scale(0.5))
        self.wait(1)


class RectangleGrowing(Scene):
    """Scene that creates and grows a rectangle"""
    def construct(self):
        rectangle = Rectangle(width=4, height=2, color=RED)
        self.play(Create(rectangle))
        self.play(rectangle.animate.scale(1.5))
        self.wait(1)


class TriangleRotating(Scene):
    """Scene that creates and rotates a triangle"""
    def construct(self):
        triangle = Triangle(color=GREEN)
        self.play(Create(triangle))
        self.play(triangle.animate.rotate(PI))
        self.wait(1)


class StarPulsing(Scene):
    """Scene that creates a star and makes it pulse"""
    def construct(self):
        star = Star(color=YELLOW)
        self.play(Create(star))
        for _ in range(3):
            self.play(star.animate.scale(1.2), run_time=0.3)
            self.play(star.animate.scale(1/1.2), run_time=0.3)
        self.wait(1)


class MultiShapeSequence(Scene):
    """Scene that displays multiple shapes in sequence"""
    def construct(self):
        shapes = [
            (Circle(color=BLUE), "Circle"),
            (Square(color=RED), "Square"),
            (Triangle(color=GREEN), "Triangle"),
            (Star(color=YELLOW), "Star")
        ]
        
        for shape, name in shapes:
            label = Text(name, font_size=24)
            self.play(Create(shape))
            self.play(Write(label))
            self.wait(0.5)
            self.play(FadeOut(shape), FadeOut(label))
