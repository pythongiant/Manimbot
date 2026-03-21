from manim import *
import numpy as np


# ============================================================================
# Mathematical Concepts with Multiple Scenes
# ============================================================================


class IntroductionScene(Scene):
    """Introduction slide for the mathematical concept"""
    def construct(self):
        title = Text("Mathematical Concepts", font_size=48, color=BLUE)
        subtitle = Text("A Visual Exploration", font_size=32, color=GREY)
        
        self.play(Write(title))
        self.play(FadeIn(subtitle))
        subtitle.next_to(title, DOWN, buff=0.5)
        self.wait(2)


class SineWaveScene(Scene):
    """Demonstrates the sine wave function"""
    def construct(self):
        axes = Axes(
            x_range=[-2*PI, 2*PI, PI/2],
            y_range=[-2, 2, 1],
            axis_config={"color": GREY_A},
            tips=False,
        )
        
        sine_curve = axes.plot(lambda x: np.sin(x), color=BLUE_C)
        sine_label = axes.get_graph_label(sine_curve, label=r'\sin(x)')
        
        title = Text("Sine Wave", font_size=32, color=BLUE)
        title.to_edge(UP)
        
        self.add(title)
        self.play(Create(axes), run_time=1)
        self.play(Create(sine_curve), Write(sine_label), run_time=2)
        self.wait(2)


class CosineWaveScene(Scene):
    """Demonstrates the cosine wave function"""
    def construct(self):
        axes = Axes(
            x_range=[-2*PI, 2*PI, PI/2],
            y_range=[-2, 2, 1],
            axis_config={"color": GREY_A},
            tips=False,
        )
        
        cosine_curve = axes.plot(lambda x: np.cos(x), color=GREEN_C)
        cosine_label = axes.get_graph_label(cosine_curve, label=r'\cos(x)')
        
        title = Text("Cosine Wave", font_size=32, color=GREEN)
        title.to_edge(UP)
        
        self.add(title)
        self.play(Create(axes), run_time=1)
        self.play(Create(cosine_curve), Write(cosine_label), run_time=2)
        self.wait(2)


class TangentWaveScene(Scene):
    """Demonstrates the tangent wave function"""
    def construct(self):
        axes = Axes(
            x_range=[-PI, PI, PI/4],
            y_range=[-5, 5, 1],
            axis_config={"color": GREY_A},
            tips=False,
        )
        
        def safe_tan(x):
            # Avoid discontinuities
            return np.tan(np.clip(x, -PI/2.1, PI/2.1))
        
        tangent_curve = axes.plot(safe_tan, color=RED_C)
        tangent_label = axes.get_graph_label(tangent_curve, label=r'\tan(x)', x_val=0)
        
        title = Text("Tangent Wave", font_size=32, color=RED)
        title.to_edge(UP)
        
        self.add(title)
        self.play(Create(axes), run_time=1)
        self.play(Create(tangent_curve), Write(tangent_label), run_time=2)
        self.wait(2)


class ComparisonScene(Scene):
    """Compares all three trigonometric functions"""
    def construct(self):
        axes = Axes(
            x_range=[-2*PI, 2*PI, PI/2],
            y_range=[-2, 2, 1],
            axis_config={"color": GREY_A},
            tips=False,
        )
        
        sine = axes.plot(lambda x: np.sin(x), color=BLUE_C)
        cosine = axes.plot(lambda x: np.cos(x), color=GREEN_C)
        
        sine_label = Text(r"sin(x)", font_size=20, color=BLUE_C)
        cosine_label = Text(r"cos(x)", font_size=20, color=GREEN_C)
        
        sine_label.next_to(axes, UP)
        cosine_label.next_to(sine_label, RIGHT)
        
        title = Text("Trigonometric Comparison", font_size=32, color=PURPLE)
        title.to_edge(UP)
        
        self.add(title)
        self.play(Create(axes), run_time=1)
        self.play(Create(sine), Write(sine_label), run_time=1)
        self.play(Create(cosine), Write(cosine_label), run_time=1)
        self.wait(2)


class ConclusionScene(Scene):
    """Conclusion slide"""
    def construct(self):
        text = Text("The Beauty of Mathematics", font_size=40, color=PURPLE)
        self.play(Write(text))
        self.wait(2)
