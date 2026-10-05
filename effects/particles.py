"""
effects/particles.py
Procedural particle system — NumPy-accelerated for real-time-ish frame generation.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

class ParticleSystem:
    def __init__(self, width, height, count=120, seed=42):
        self.W = width
        self.H = height
        self.N = count
        rng = np.random.default_rng(seed)

        # Position
        self.x = rng.uniform(0, width,  count).astype(np.float32)
        self.y = rng.uniform(0, height, count).astype(np.float32)

        # Velocity (very slow — atmospheric)
        self.vx = rng.uniform(-0.15, 0.15, count).astype(np.float32)
        self.vy = rng.uniform(-0.35, -0.05, count).astype(np.float32)  # drift upward

        # Depth / parallax  (0=far, 1=near)
        self.depth = rng.uniform(0.1, 1.0, count).astype(np.float32)

        # Size (radius in px)
        self.size = (rng.uniform(0.5, 2.5, count) * self.depth).astype(np.float32)

        # Base opacity
        self.base_alpha = rng.uniform(30, 140, count).astype(np.float32)

        # Phase offset for twinkling
        self.phase = rng.uniform(0, 2 * np.pi, count).astype(np.float32)
        self.twinkle_speed = rng.uniform(0.3, 1.2, count).astype(np.float32)

    def step(self, t: float, cam_x: float = 0, cam_y: float = 0):
        """Advance simulation by one frame."""
        # Parallax offset: near particles move more with camera
        px = self.x + cam_x * self.depth * 0.4
        py = self.y + cam_y * self.depth * 0.4

        # Twinkling
        tw = 0.6 + 0.4 * np.sin(self.phase + t * self.twinkle_speed)

        # Alive-ness check: wrap particles
        self.x += self.vx
        self.y += self.vy
        # wrap-around
        self.x[self.x < -5] += self.W + 10
        self.x[self.x > self.W + 5] -= self.W + 10
        self.y[self.y < -5] = self.H + 5

        return px, py, tw

    def render(self, t: float, cam_x: float = 0, cam_y: float = 0,
               color=(99, 179, 237), alpha_scale: float = 1.0) -> Image.Image:
        """Return RGBA layer with particles drawn on transparent bg."""
        img = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        px, py, tw = self.step(t, cam_x, cam_y)
        alphas = np.clip(self.base_alpha * tw * alpha_scale, 0, 255).astype(int)

        for i in range(self.N):
            a = int(alphas[i])
            if a < 5:
                continue
            r = max(0.8, float(self.size[i]))
            cx, cy = float(px[i]), float(py[i])
            # Soft atmospheric particle: outer faint halo + inner core
            outer_r = r * 2.2
            draw.ellipse([cx - outer_r, cy - outer_r, cx + outer_r, cy + outer_r],
                         fill=(*color, max(1, a // 4)))
            draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                         fill=(*color, a))

        return img
