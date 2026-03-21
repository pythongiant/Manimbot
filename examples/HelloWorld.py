from manim import *

class HelloWorld(Scene):
    def construct(self):
        text = Text("Hello world", font_size=144)
        self.add(text)
