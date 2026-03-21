from manim import *

class PieChart(Scene):
    def construct(self):
        # Create pie chart data
        data = [30, 25, 20, 25]
        labels = ["A", "B", "C", "D"]
        colors = [BLUE, GREEN, RED, YELLOW]
        
        # Create pie slices
        slices = VGroup()
        start_angle = 0
        
        for i, (value, label, color) in enumerate(zip(data, labels, colors)):
            angle = (value / sum(data)) * 2 * PI
            
            # Create slice as a wedge\n            arc = Arc(
                angle=angle,\n                radius=2,
                arc_center=ORIGIN,
                color=color,
                stroke_width=2
            )
            line1 = Line(ORIGIN, 2 * np.array([np.cos(start_angle), np.sin(start_angle), 0]), color=color)
            line2 = Line(ORIGIN, 2 * np.array([np.cos(start_angle + angle), np.sin(start_angle + angle), 0]), color=color)
            
            label_obj = Text(label, color=WHITE, font_size=24)
            label_angle = start_angle + angle / 2
            label_obj.shift(1.2 * np.array([np.cos(label_angle), np.sin(label_angle), 0]))
            
            slices.add(line1, arc, line2, label_obj)
            start_angle += angle
        
        self.play(Create(slices), run_time=2)
        self.wait(2)
