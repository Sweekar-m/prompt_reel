"""
engine/metaphor_renderer.py
===========================
Procedural Visual Metaphor Rendering Engine.
Renders tactile, physical 2.5D and schematic metaphors for abstract CS concepts:
1. physical_stack: Stack of 3D isometric blocks with push/pop dynamics (Recursion)
2. janitor_laser: Laser sweeper vaporizing orphaned memory nodes (Garbage Collection)
3. restaurant_queue: Ticket rail with non-blocking async event loops (Async/Await)
4. memory_shelf: Instant desk shelf vs distant warehouse (Cache vs RAM)
5. narrowing_corridor: Slicing blast doors closing off 50% at each step (Binary Search)
6. pointer_arrows: Luminous vector cables linking addresses (Pointers)
7. worker_conveyor: Parallel robotic assembly tracks with mutex lights (Threads)
8. tabbed_book_index: Indexed encyclopedic volume with thumb tabs (Database Index)
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from typing import Tuple, Dict, Any, Optional

RGBColor = Tuple[int, int, int]


def render_metaphor_frame(
    metaphor_id: str,
    progress: float,          # 0.0 to 1.0 within the metaphor beat
    canvas_size: Tuple[int, int] = (1080, 1920),
    primary_color: RGBColor = (0, 240, 255),
    secondary_color: RGBColor = (255, 110, 90),
    accent_color: RGBColor = (255, 210, 70),
    surface_color: RGBColor = (20, 24, 36),
    font: Optional[ImageFont.FreeTypeFont] = None
) -> Image.Image:
    """Renders a procedural visual metaphor layer on transparent RGBA canvas."""
    W, H = canvas_size
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    mid_x = W // 2
    mid_y = H // 2 + 100

    if metaphor_id == "physical_stack":
        # ── Stack of 3D Isometric Acrylic Blocks ──────────────────────────────
        total_blocks = 5
        active_count = min(int(progress * (total_blocks + 2)), total_blocks)
        is_unwinding = progress > 0.65
        unwind_p = (progress - 0.65) / 0.35 if is_unwinding else 0.0

        block_w = 420
        block_h = 75
        iso_dy = 28
        base_y = mid_y + 220

        # Draw base pedestal
        draw.polygon([
            (mid_x - 260, base_y),
            (mid_x, base_y - 45),
            (mid_x + 260, base_y),
            (mid_x, base_y + 45)
        ], fill=(*surface_color, 220), outline=(*secondary_color, 180))

        for i in range(total_blocks):
            if i < active_count:
                by = base_y - 40 - (i * (block_h + 12))
                # Fade out if unwinding
                alpha = 255
                if is_unwinding and i >= int((1.0 - unwind_p) * total_blocks):
                    alpha = max(0, int((1.0 - (unwind_p * 3)) * 255))
                    by -= int(unwind_p * 80)

                col = primary_color if i == active_count - 1 else secondary_color

                # Isometric top face
                draw.polygon([
                    (mid_x - block_w // 2, by),
                    (mid_x, by - iso_dy),
                    (mid_x + block_w // 2, by),
                    (mid_x, by + iso_dy)
                ], fill=(col[0], col[1], col[2], int(alpha * 0.7)), outline=(col[0], col[1], col[2], alpha))

                # Front-left face
                draw.polygon([
                    (mid_x - block_w // 2, by),
                    (mid_x, by + iso_dy),
                    (mid_x, by + iso_dy + block_h),
                    (mid_x - block_w // 2, by + block_h)
                ], fill=(int(col[0] * 0.5), int(col[1] * 0.5), int(col[2] * 0.5), alpha), outline=(*col, alpha))

                # Front-right face
                draw.polygon([
                    (mid_x, by + iso_dy),
                    (mid_x + block_w // 2, by),
                    (mid_x + block_w // 2, by + block_h),
                    (mid_x, by + iso_dy + block_h)
                ], fill=(int(col[0] * 0.7), int(col[1] * 0.7), int(col[2] * 0.7), alpha), outline=(*col, alpha))

                # Block label
                if font:
                    label = f"FRAME #{i+1} [n={total_blocks - i}]"
                    draw.text((mid_x - 110, by + block_h // 3), label, fill=(255, 255, 255, alpha), font=font)

    elif metaphor_id == "narrowing_corridor":
        # ── Binary Search Blast Doors ─────────────────────────────────────────
        corridor_w = 700
        corridor_h = 600
        top_y = mid_y - corridor_h // 2

        # Outer corridor tunnel
        draw.rectangle([mid_x - corridor_w // 2, top_y, mid_x + corridor_w // 2, top_y + corridor_h],
                       fill=(*surface_color, 230), outline=(*primary_color, 120), width=3)

        # Draw 5 division gates
        stages = 4
        for s in range(stages):
            split_p = min(max((progress - s * 0.22) / 0.22, 0.0), 1.0)
            if split_p > 0.05:
                # Seal off one side with hazard stripes
                door_side = (s % 2 == 0)
                door_w = int((corridor_w // (2 ** (s + 1))) * split_p)
                door_x = mid_x - corridor_w // 2 if door_side else mid_x + corridor_w // 2 - door_w
                dy = top_y + s * (corridor_h // stages)
                dh = corridor_h // stages

                # Sealed off door block
                draw.rectangle([door_x, dy, door_x + door_w, dy + dh],
                               fill=(int(secondary_color[0] * 0.4), int(secondary_color[1] * 0.4), int(secondary_color[2] * 0.4), 190),
                               outline=(*secondary_color, 240), width=2)
                # Strikethrough hazard line
                draw.line([(door_x, dy), (door_x + door_w, dy + dh)], fill=(*secondary_color, 220), width=2)

        # Target beacon in the remaining pocket
        beacon_radius = 28 + int(8 * math.sin(progress * 15))
        draw.ellipse([mid_x - beacon_radius, mid_y - beacon_radius, mid_x + beacon_radius, mid_y + beacon_radius],
                     fill=(*accent_color, 240), outline=(255, 255, 255, 255), width=3)

    elif metaphor_id == "janitor_laser":
        # ── Memory Cells Sweeper ──────────────────────────────────────────────
        grid_cols, grid_rows = 5, 4
        cell_size = 110
        start_x = mid_x - (grid_cols * (cell_size + 16)) // 2
        start_y = mid_y - (grid_rows * (cell_size + 16)) // 2

        sweep_x = start_x + int(progress * (grid_cols * (cell_size + 16) + 60))

        for r in range(grid_rows):
            for c in range(grid_cols):
                cx = start_x + c * (cell_size + 16)
                cy = start_y + r * (cell_size + 16)
                is_garbage = ((r + c * 3) % 3 == 0)

                if is_garbage and cx < sweep_x:
                    # Cleaned/vaporized
                    col = (*surface_color, 80)
                    draw.rectangle([cx, cy, cx + cell_size, cy + cell_size], fill=col, outline=(50, 60, 80, 80))
                elif is_garbage:
                    # Orphaned (marked red)
                    draw.rectangle([cx, cy, cx + cell_size, cy + cell_size],
                                   fill=(*secondary_color, 160), outline=(*secondary_color, 255), width=2)
                else:
                    # Active referenced memory (cyan)
                    draw.rectangle([cx, cy, cx + cell_size, cy + cell_size],
                                   fill=(*primary_color, 160), outline=(*primary_color, 255), width=2)

        # Laser beam
        draw.line([(sweep_x, start_y - 40), (sweep_x, start_y + grid_rows * (cell_size + 16) + 40)],
                  fill=(*accent_color, 255), width=6)

    elif metaphor_id == "pointer_arrows":
        # ── Luminous Address Cables ───────────────────────────────────────────
        stack_x = mid_x - 300
        heap_x = mid_x + 180
        nodes = 4
        for n in range(nodes):
            sy = mid_y - 200 + n * 110
            hy = mid_y - 200 + ((n * 2) % nodes) * 110

            # Stack slot
            draw.rectangle([stack_x, sy, stack_x + 120, sy + 70],
                           fill=(*surface_color, 230), outline=(*primary_color, 200), width=2)
            # Heap slot
            draw.rectangle([heap_x, hy, heap_x + 160, hy + 70],
                           fill=(*surface_color, 230), outline=(*secondary_color, 200), width=2)

            # Curved dynamic laser cable
            cable_p = min(max((progress - n * 0.15) / 0.4, 0.0), 1.0)
            if cable_p > 0.05:
                curr_hx = stack_x + 120 + int((heap_x - (stack_x + 120)) * cable_p)
                curr_hy = sy + int((hy - sy) * cable_p)
                draw.line([(stack_x + 120, sy + 35), (curr_hx, curr_hy + 35)],
                          fill=(*accent_color, int(cable_p * 255)), width=3)
                # Arrowhead
                if cable_p > 0.95:
                    draw.polygon([
                        (curr_hx, curr_hy + 35),
                        (curr_hx - 12, curr_hy + 27),
                        (curr_hx - 12, curr_hy + 43)
                    ], fill=(*accent_color, 255))

    else:
        # ── Default: Tabbed Index Book ────────────────────────────────────────
        book_w, book_h = 560, 480
        bx = mid_x - book_w // 2
        by = mid_y - book_h // 2

        # Book covers
        draw.rectangle([bx, by, bx + book_w, by + book_h],
                       fill=(*surface_color, 240), outline=(*primary_color, 180), width=3)

        # Tab dividers on the right
        num_tabs = 5
        tab_h = book_h // num_tabs
        active_tab = min(int(progress * num_tabs), num_tabs - 1)
        for t_idx in range(num_tabs):
            ty = by + t_idx * tab_h
            is_active = (t_idx == active_tab)
            t_col = accent_color if is_active else secondary_color
            t_w = 45 if is_active else 25
            draw.rectangle([bx + book_w, ty + 6, bx + book_w + t_w, ty + tab_h - 6],
                           fill=(*t_col, 240), outline=(*t_col, 255))

        # Central spine
        draw.line([(mid_x, by), (mid_x, by + book_h)], fill=(*primary_color, 160), width=3)

    return layer
