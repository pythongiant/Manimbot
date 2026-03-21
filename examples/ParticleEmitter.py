from manim import *
import numpy as np

class ParticleEmitter(Scene):
    def construct(self):
        # Create particles
        particles = VGroup()\n        for i in range(50):
            particle = Circle(radius=0.05, color=random_color())
            particle.shift(np.random.uniform(-3, 3, 3))
            particles.add(particle)
        
        self.add(particles)
        
        # Animate particles
        def particle_motion(mob, alpha):
            angle = np.random.uniform(0, 2 * PI)\n            speed = 0.05
            displacement = np.array([
                np.cos(angle) * speed,
                np.sin(angle) * speed,
                0
            ])
            mob.shift(displacement * 50)
        
        # Fade and move particles
        self.play(Create(particles), run_time=0.5)
        self.wait(1)
        self.play(FadeOut(particles), run_time=2)
