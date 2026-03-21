from manim import *
import numpy as np

class SortingVisualization(Scene):
    def construct(self):
        # Create random bars
        np.random.seed(42)
        arr = np.random.randint(1, 10, 10)
        
        # Create bar chart
        bars = VGroup()
        for i, val in enumerate(arr):
            bar = Rectangle(width=0.4, height=val * 0.5, color=BLUE)
            bar.shift(RIGHT * (i - 4.5))
            bars.add(bar)
        
        self.add(bars)
        
        # Simple bubble sort animation
        for i in range(len(arr)):
            for j in range(len(arr) - 1 - i):
                if arr[j] > arr[j + 1]:
                    # Swap
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
                    # Animate swap
                    self.play(
                        bars[j].animate.shift(RIGHT * 0.4),
                        bars[j + 1].animate.shift(LEFT * 0.4),
                        run_time=0.3
                    )
                    # Swap in VGroup
                    bars[j], bars[j + 1] = bars[j + 1], bars[j]
