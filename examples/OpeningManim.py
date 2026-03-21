from manim import *

class OpeningManim(Scene):
    def construct(self):
        title = Tex(r"This is some \LaTeX")
        formula = MathTex(r"\sum_{n=1}^\infty \frac{1}{n^2} = \frac{\pi^2}{6}")
        VGroup(title, formula).arrange(DOWN)

        self.play(Write(title))
        self.play(FadeIn(formula, shift=DOWN))
        self.wait()
