from manim import *

class TextAnimations(Scene):
    def construct(self):
        # Create title
        title = Text("Text Animations", font_size=48, color=BLUE)
        self.add(title)
        
        # Animate title entrance
        self.play(FadeIn(title), title.animate.to_edge(UP), run_time=1)
        
        # Create various text animations
        text1 = Text("Fade In", font_size=32)
        text1.shift(UP * 2)
        self.play(FadeIn(text1), run_time=1)
        
        text2 = Text("Scale Up", font_size=32)
        text2.shift(UP)
        self.play(GrowFromCenter(text2), run_time=1)
        
        text3 = Text("Write", font_size=32)
        text3.shift(DOWN)
        self.play(Write(text3), run_time=1)
        
        text4 = Text("Spiral In", font_size=32)
        text4.shift(DOWN * 2)
        self.play(GrowFromPoint(text4, ORIGIN), run_time=1)
        
        # Group all texts
        all_texts = VGroup(text1, text2, text3, text4)
        
        # Animate all together
        self.wait(1)
        self.play(all_texts.animate.scale(1.2).set_color(YELLOW), run_time=1)
        self.play(all_texts.animate.rotate(PI/6), run_time=1)
        self.play(FadeOut(all_texts), run_time=1)
