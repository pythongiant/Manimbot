from manim import *
import numpy as np

class LorentzAttractor(Scene):
    def construct(self):
        axes = ThreeDAxes()
        
        # Define Lorenz system
        def lorenz_eq(point, sigma=10, rho=28, beta=8/3):
            x, y, z = point
            dx = sigma * (y - x)
            dy = x * (rho - z) - y
            dz = x * y - beta * z
            return np.array([dx, dy, dz])
        
        # Solve using simple Euler method
        points = [np.array([1, 1, 1])]
        dt = 0.001
        for _ in range(10000):
            point = points[-1]
            next_point = point + lorenz_eq(point) * dt
            points.append(next_point)
        
        # Create curve from points (sample every 50th point for performance)
        sampled_points = points[::50]
        curve_points = np.array(sampled_points)
        
        # Create parametric curve
        curve = VMobject()
        curve.set_points_as_corners(curve_points)
        curve.set_color_by_gradient(BLUE, PURPLE, RED)
        curve.set_stroke(width=1)
        
        self.add(axes)
        self.add(curve)
        self.move_camera(phi=60*DEGREES, theta=45*DEGREES)
        self.wait(3)
