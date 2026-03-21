from manim import *

class MatrixTransformation(Scene):
    def construct(self):
        # Create matrix\n        matrix = Matrix(
            [[1, 2],
             [3, 4]],
            mat_brackets_num_rows=2,
            h_buff=1.5
        )
        
        # Create vector
        vec = Matrix([[2], [1]], h_buff=1.2)
        vec.next_to(matrix, RIGHT, buff=1)
        
        # Create result label
        equals = MathTex("=").next_to(vec, RIGHT, buff=0.5)
        result = Matrix([[4], [10]], h_buff=1.2)
        result.next_to(equals, RIGHT, buff=0.5)
        
        # Animate
        self.play(Create(matrix), Write(vec))
        self.wait(1)
        
        # Show transformation
        self.play(Write(equals), Create(result), run_time=2)
        self.wait(2)
