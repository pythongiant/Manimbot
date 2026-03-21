from manim import *

class LatexRendering(Scene):
    def construct(self):
        # Create various LaTeX equations
        eq1 = MathTex(r"\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}")
        eq2 = MathTex(r"e^{i\pi} + 1 = 0")
        eq3 = MathTex(r"\frac{-b \pm \sqrt{b^2 - 4ac}}{2a}")
        
        # Position equations
        eq1.shift(UP * 2)
        eq2.shift(DOWN * 1)
        eq3.shift(DOWN * 4)
        
        # Animate equations
        self.play(Write(eq1))
        self.wait(1)
        self.play(FadeIn(eq2))
        self.wait(1)
        self.play(Transform(eq2, eq3))
        self.wait(2)
