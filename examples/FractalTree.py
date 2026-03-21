from manim import *

class FractalTree(Scene):
    def construct(self):
        def create_tree(start, direction, depth, scale, color):
            if depth == 0:
                return VGroup()
            
            end = start + direction * scale
            line = Line(start, end, color=color, stroke_width=2)
            
            tree = VGroup(line)
            
            # Create two branches
            angle_offset = PI / 6
            for offset in [-angle_offset, angle_offset]:
                rotated_dir = np.array([
                    direction[0] * np.cos(offset) - direction[1] * np.sin(offset),
                    direction[0] * np.sin(offset) + direction[1] * np.cos(offset),
                    0
                ])
                tree.add(create_tree(
                    end, 
                    rotated_dir, 
                    depth - 1, 
                    scale * 0.8,
                    color
                ))
            
            return tree
        
        # Create the tree
        initial_direction = np.array([0, 1, 0])
        tree = create_tree(ORIGIN, initial_direction, 8, 1, GREEN)
        
        # Animate
        self.play(Create(tree), run_time=3)
        self.wait(2)
