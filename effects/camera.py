"""
effects/camera.py
Virtual cinematic camera with smooth interpolation.
"""
import math

class Camera:
    def __init__(self, width, height):
        self.W = width
        self.H = height
        self.x = 0.0        # pan offset (pixels)
        self.y = 0.0
        self.zoom = 1.0
        self.rotation = 0.0

        # Target values for smooth interpolation
        self._tx = 0.0
        self._ty = 0.0
        self._tz = 1.0
        self._tr = 0.0

        self.smoothing = 0.08

    # ── setters ──────────────────────────────────────────────────────────────
    def set_target(self, x=None, y=None, zoom=None, rotation=None):
        if x        is not None: self._tx = x
        if y        is not None: self._ty = y
        if zoom     is not None: self._tz = zoom
        if rotation is not None: self._tr = rotation

    # ── per-frame update ──────────────────────────────────────────────────────
    def update(self, shake: float = 0.0):
        s = self.smoothing
        self.x        += (self._tx - self.x)        * s
        self.y        += (self._ty - self.y)        * s
        self.zoom     += (self._tz - self.zoom)     * s
        self.rotation += (self._tr - self.rotation) * s

        if shake > 0:
            import random
            self.x += random.uniform(-shake, shake)
            self.y += random.uniform(-shake, shake)

    # ── apply to PIL image ────────────────────────────────────────────────────
    def apply(self, img):
        if abs(self.zoom - 1.0) < 0.002 and abs(self.x) < 0.5 and abs(self.y) < 0.5 and abs(self.rotation) < 0.01:
            return img
        from PIL import Image
        w, h = img.size
        # Zoom: crop center then resize back
        new_w = int(w / self.zoom)
        new_h = int(h / self.zoom)
        new_w = max(10, new_w)
        new_h = max(10, new_h)

        ox = int(w / 2 - new_w / 2 + self.x)
        oy = int(h / 2 - new_h / 2 + self.y)
        ox = max(0, min(ox, w - new_w))
        oy = max(0, min(oy, h - new_h))

        crop = img.crop((ox, oy, ox + new_w, oy + new_h))
        resized = crop.resize((w, h), Image.BILINEAR)

        if abs(self.rotation) > 0.01:
            resized = resized.rotate(self.rotation, expand=False,
                                     resample=Image.BILINEAR)
        return resized


# Pre-defined camera keyframes per scene
def get_camera_keyframes(scene: str):
    """
    Returns a list of (t_norm, x, y, zoom, rotation) keyframes.
    t_norm is 0..1 within the scene.
    """
    presets = {
        "hook": [
            (0.0,  0,  0, 1.00, 0.0),
            (0.5,  0, -8, 1.04, 0.0),
            (1.0,  0, -4, 1.06, 0.0),
        ],
        "curiosity": [
            (0.0,  0,  0, 1.06, 0.0),
            (0.5,  0,  0, 1.10, 0.0),
            (1.0,  0,  0, 1.12, 0.0),
        ],
        "step1": [
            (0.0,  0,  0, 1.08, 0.0),
            (0.5,  0,  5, 1.10, 0.0),
            (1.0,  0,  0, 1.08, 0.0),
        ],
        "step2": [
            (0.0,  0,  0, 1.05, 0.0),
            (0.5,  0, -5, 1.08, 0.0),
            (1.0,  0,  0, 1.05, 0.0),
        ],
        "step3": [
            (0.0,  0,  0, 1.06, 0.0),
            (0.5,  8,  0, 1.09, 0.2),
            (1.0,  0,  0, 1.06, 0.0),
        ],
        "payoff": [
            (0.0,  0,  0, 1.04, 0.0),
            (0.5,  0, -6, 1.08, 0.0),
            (1.0,  0, -3, 1.06, 0.0),
        ],
        "loop": [
            (0.0,  0, -3, 1.06, 0.0),
            (0.5,  0,  0, 1.03, 0.0),
            (1.0,  0,  0, 1.00, 0.0),
        ],
    }
    return presets.get(scene, [(0.0, 0, 0, 1.0, 0.0), (1.0, 0, 0, 1.0, 0.0)])


def interpolate_camera(keyframes, t_norm: float):
    """Linear interpolation between keyframes."""
    if t_norm <= keyframes[0][0]:
        return keyframes[0][1:]
    if t_norm >= keyframes[-1][0]:
        return keyframes[-1][1:]

    for i in range(len(keyframes) - 1):
        t0, *v0 = keyframes[i]
        t1, *v1 = keyframes[i + 1]
        if t0 <= t_norm <= t1:
            alpha = (t_norm - t0) / (t1 - t0)
            # smooth step
            alpha = alpha * alpha * (3 - 2 * alpha)
            result = tuple(a + (b - a) * alpha for a, b in zip(v0, v1))
            return result
    return keyframes[-1][1:]
