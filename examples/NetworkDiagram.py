from manim import *

class NetworkDiagram(Scene):
    def construct(self):
        # Create nodes
        nodes = VGroup()\n        for i in range(5):
            angle = 2 * PI * i / 5
            node = Circle(radius=0.3, color=BLUE)
            node.shift(2 * np.array([np.cos(angle), np.sin(angle), 0]))
            nodes.add(node)
        
        # Add center node
        center = Circle(radius=0.3, color=RED)
        nodes.add(center)
        
        # Create edges
        edges = VGroup()
        for i in range(5):
            edge = Line(nodes[i].get_center(), nodes[5].get_center(), color=GREY)
            edges.add(edge)
        
        # Animate
        self.play(Create(nodes), Create(edges), run_time=2)
        
        # Add labels
        labels = VGroup()
        for i, node in enumerate(nodes):
            label = Integer(i).scale(0.8)
            label.move_to(node)
            labels.add(label)
        
        self.play(Write(labels), run_time=1)
        self.wait(2)
