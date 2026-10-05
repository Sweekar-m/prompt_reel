"""
engine/math_3d_renderer.py
==========================
Procedural 2D-to-3D Mathematical Projection Engine for Python Fallback Renderer.
Renders 2D Cartesian function curves smoothly tilting and elevating into
orbiting 3D isometric parametric surface wireframes with real-time HUD telemetry.
"""
import math
from PIL import Image, ImageDraw, ImageFont
from typing import Tuple, Dict, Any, Optional

RGBColor = Tuple[int, int, int]


def render_math_3d_frame(
    progress: float,          # 0.0 to 1.0 within the math beat
    canvas_size: Tuple[int, int] = (1080, 1920),
    primary_color: RGBColor = (0, 240, 255),
    secondary_color: RGBColor = (168, 85, 247),
    accent_color: RGBColor = (245, 158, 11),
    surface_color: RGBColor = (18, 20, 28),
    title: str = "2D TO 3D MATHEMATICAL PROJECTION",
    equation: str = "$z = \\sin(\\sqrt{x^2+y^2}) / \\sqrt{x^2+y^2}$",
    formula_2d: str = "$y = \\sin(x)/x$",
    function_type: str = "sinc",
    font_mono: Optional[ImageFont.FreeTypeFont] = None,
    font_heading: Optional[ImageFont.FreeTypeFont] = None
) -> Image.Image:
    """Renders a procedural 2D to 3D math layer with dynamic camera perspective on RGBA canvas."""
    W, H = canvas_size
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    scale_f = W / 1080.0
    cx = W // 2
    cy = int(H * 0.58)

    # Transition timing:
    # Phase 1: 0.0 to 0.30 (flat 2D view)
    # Phase 2: 0.30 to 0.65 (smooth camera tilt and yaw into 3D)
    # Phase 3: 0.65 to 1.0 (continuous 3D orbital drift)
    if progress < 0.28:
        pitch_deg = 0.0
        yaw_deg = 0.0
        mesh_extrude = 0.0
        mode_text = "2D CARTESIAN CROSS-SECTION"
    elif progress < 0.62:
        t_trans = (progress - 0.28) / (0.62 - 0.28)
        # Smooth ease-in-out cubic
        ease = 3 * t_trans**2 - 2 * t_trans**3
        pitch_deg = ease * 52.0
        yaw_deg = ease * 38.0
        mesh_extrude = ease
        mode_text = "CAMERA PITCH ➔ 3D ISOMETRIC TRANSITION"
    else:
        t_orbit = (progress - 0.62) / (1.0 - 0.62)
        pitch_deg = 52.0 + t_orbit * 6.0
        yaw_deg = 38.0 + t_orbit * 36.0
        mesh_extrude = 1.0
        mode_text = "3D TENSOR FIELD ORBIT"

    pitch_rad = math.radians(pitch_deg)
    yaw_rad = math.radians(yaw_deg)
    time_offset = progress * 6.28

    proj_scale = 135 * scale_f

    def project_point(x: float, y: float, z: float) -> Tuple[int, int, float]:
        # 1. Yaw rotation (around Z)
        x1 = x * math.cos(yaw_rad) - y * math.sin(yaw_rad)
        y1 = x * math.sin(yaw_rad) + y * math.cos(yaw_rad)

        # 2. Pitch rotation (tilt down)
        y2 = y1 * math.cos(pitch_rad) - z * math.sin(pitch_rad)
        z2 = y1 * math.sin(pitch_rad) + z * math.cos(pitch_rad)

        # Perspective scaling
        fov = 700.0
        p = fov / (fov + z2 * proj_scale * 0.28)

        u = int(cx + x1 * proj_scale * p)
        v = int(cy - y2 * proj_scale * p)
        return (u, v, z2)

    def eval_z(x: float, y: float) -> float:
        if function_type == "saddle":
            return (x**2 - y**2) * 0.22 * mesh_extrude
        elif function_type == "euler_helix":
            r = math.sqrt(x**2 + y**2)
            return math.sin(r * 2.8 - time_offset) * 0.7 * mesh_extrude
        else:
            r = math.sqrt(x**2 + y**2) * 2.6 + 1e-4
            return (math.sin(r - time_offset) / r) * 1.25 * mesh_extrude

    # Draw 3D Viewport Box
    box_w = int(W * 0.88)
    box_h = int(H * 0.44)
    box_x = (W - box_w) // 2
    box_y = cy - box_h // 2
    draw.rectangle(
        [box_x, box_y, box_x + box_w, box_y + box_h],
        fill=(*surface_color, 210),
        outline=(*accent_color, 120),
        width=max(1, int(2 * scale_f))
    )

    # Draw Coordinate Axes
    extent = 2.2
    origin = project_point(0, 0, 0)
    ax_x = project_point(extent * 1.15, 0, 0)
    ax_y = project_point(0, extent * 1.15, 0)
    ax_z = project_point(0, 0, 1.2)

    # X axis (Cyan)
    draw.line([(origin[0], origin[1]), (ax_x[0], ax_x[1])], fill=(*primary_color, 200), width=max(1, int(2 * scale_f)))
    if font_mono:
        draw.text((ax_x[0] + 6, ax_x[1] - 8), "+X", fill=(*primary_color, 240), font=font_mono)

    # Y axis (Purple)
    draw.line([(origin[0], origin[1]), (ax_y[0], ax_y[1])], fill=(*secondary_color, 200), width=max(1, int(2 * scale_f)))
    if font_mono:
        draw.text((ax_y[0] + 6, ax_y[1] - 8), "+Y", fill=(*secondary_color, 240), font=font_mono)

    # Z axis (Amber - emerges in 3D)
    if mesh_extrude > 0.05:
        z_alpha = int(mesh_extrude * 255)
        draw.line([(origin[0], origin[1]), (ax_z[0], ax_z[1])], fill=(*accent_color, z_alpha), width=max(2, int(3 * scale_f)))
        if font_mono:
            draw.text((ax_z[0] + 6, ax_z[1] - 8), "+Z", fill=(*accent_color, z_alpha), font=font_mono)

    # Draw 3D Wireframe Grid Mesh
    grid_n = 14
    step = (extent * 2) / grid_n
    mesh_lines = []

    # Rows (along X)
    for i in range(grid_n + 1):
        x = -extent + i * step
        row_pts = []
        for j in range(grid_n + 1):
            y = -extent + j * step
            z = eval_z(x, y)
            row_pts.append(project_point(x, y, z))
        mesh_lines.append(row_pts)

    # Columns (along Y)
    for j in range(grid_n + 1):
        y = -extent + j * step
        col_pts = []
        for i in range(grid_n + 1):
            x = -extent + i * step
            z = eval_z(x, y)
            col_pts.append(project_point(x, y, z))
        mesh_lines.append(col_pts)

    # Render wireframe lines
    line_alpha = int(mesh_extrude * 150)
    if line_alpha > 5:
        for line in mesh_lines:
            for k in range(len(line) - 1):
                p1 = line[k]
                p2 = line[k + 1]
                # Height color blend: higher Z = brighter cyan/gold
                z_mid = (p1[2] + p2[2]) * 0.5
                if z_mid > 0.3:
                    col = (*accent_color, line_alpha)
                elif z_mid > 0.0:
                    col = (*primary_color, line_alpha)
                else:
                    col = (*secondary_color, int(line_alpha * 0.8))
                draw.line([(p1[0], p1[1]), (p2[0], p2[1])], fill=col, width=max(1, int(1.5 * scale_f)))

    # Draw 2D Cross Section Curve (thick primary curve)
    pts_2d = []
    for s in range(50):
        x = -extent + (s / 49.0) * (extent * 2)
        y = 0.0
        z = eval_z(x, y)
        pts_2d.append(project_point(x, y, z))

    for k in range(len(pts_2d) - 1):
        p1 = pts_2d[k]
        p2 = pts_2d[k + 1]
        draw.line([(p1[0], p1[1]), (p2[0], p2[1])], fill=(*primary_color, 255), width=max(2, int(4 * scale_f)))

    # Origin circle
    r = int(6 * scale_f)
    draw.ellipse([origin[0] - r, origin[1] - r, origin[0] + r, origin[1] + r], fill=(*accent_color, 255))

    # Bottom HUD Telemetry
    hud_y = box_y + box_h - int(36 * scale_f)
    draw.rectangle([box_x + 8, hud_y - 4, box_x + box_w - 8, hud_y + int(28 * scale_f)], fill=(10, 12, 18, 230))
    if font_mono:
        telemetry = f"PITCH: {pitch_deg:.1f}° | YAW: {yaw_deg:.1f}° | DIM: {'ℝ² (2D)' if progress < 0.28 else 'ℝ³ (3D TENSOR)'}"
        draw.text((box_x + int(20 * scale_f), hud_y + 2), telemetry, fill=(*accent_color, 240), font=font_mono)

    return layer
