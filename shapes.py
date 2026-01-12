from pydantic import BaseModel
import math


class ShapeSpec(BaseModel):
    shape: str
    side: float | None = None
    width: float | None = None
    height: float | None = None
    radius: float | None = None
    n_sides: int | None = None


def _svg_wrap(inner: str, canvas_px: int = 1000, stroke_width: int = 10, show_grid: bool = False) -> str:
    half = canvas_px / 2

    grid = ""
    if show_grid:
        step = 50
        # light grid (auto adapts using opacity)
        lines = []
        for x in range(int(-half), int(half) + 1, step):
            lines.append(f'<line x1="{x}" y1="{-half}" x2="{x}" y2="{half}" />')
        for y in range(int(-half), int(half) + 1, step):
            lines.append(f'<line x1="{-half}" y1="{y}" x2="{half}" y2="{y}" />')
        grid = f"""
        <g style="stroke: var(--sketch-grid); stroke-width: 1; opacity: 0.35;">
          {''.join(lines)}
        </g>
        """

    return f"""
    <div style="width:100%; display:flex; justify-content:center;">
      <style>
        :root {{
          --sketch-stroke: #111827;
          --sketch-grid: #9CA3AF;
          --sketch-bg: transparent;
        }}
        @media (prefers-color-scheme: dark) {{
          :root {{
            --sketch-stroke: #F9FAFB;
            --sketch-grid: #6B7280;
            --sketch-bg: transparent;
          }}
        }}
      </style>

      <svg width="100%" height="{canvas_px}" viewBox="{-half} {-half} {canvas_px} {canvas_px}"
           xmlns="http://www.w3.org/2000/svg"
           style="background: var(--sketch-bg); max-width: 1200px;">
        {grid}
        <g fill="none"
           style="stroke: var(--sketch-stroke);"
           stroke-width="{stroke_width}"
           stroke-linejoin="round"
           stroke-linecap="round">
          {inner}
        </g>
      </svg>
    </div>
    """


def _poly(points: list[tuple[float, float]]) -> str:
    pts = " ".join([f"{x:.2f},{y:.2f}" for x, y in points])
    return f'<polygon points="{pts}" />'


def _auto_scale(spec: ShapeSpec, fill_target: float, zoom: float = 1.0) -> float:
    """
    Treat user numbers as 'units' (not pixels) and scale them so the largest dimension ~= fill_target.
    Example: rectangle 8 by 3 -> scale ~ fill_target/8 -> big rectangle.
    """
    dims = []
    if spec.side and spec.side > 0:
        dims.append(spec.side)
    if spec.width and spec.width > 0:
        dims.append(spec.width)
    if spec.height and spec.height > 0:
        dims.append(spec.height)
    if spec.radius and spec.radius > 0:
        dims.append(2 * spec.radius)  # diameter is main dimension

    max_dim = max(dims) if dims else None
    if not max_dim:
        return 1.0 * zoom

    return (fill_target / max_dim) * zoom


def draw_shape_outline_svg(
    spec: ShapeSpec,
    canvas_px: int = 1000,
    fill_ratio: float = 0.80,   # how much of canvas the shape should occupy (0.2..0.95)
    zoom: float = 1.0,
    stroke_width: int = 10,
    show_grid: bool = False,
) -> str:
    shape = (spec.shape or "").strip().lower()

    # fill_target is in "svg pixels" inside viewBox
    fill_target = canvas_px * float(fill_ratio)
    scale = _auto_scale(spec, fill_target=fill_target, zoom=zoom)

    if shape == "square":
        s = float((spec.side or 4.0) * scale)
        half = s / 2
        pts = [(-half, -half), (half, -half), (half, half), (-half, half)]
        return _svg_wrap(_poly(pts), canvas_px=canvas_px, stroke_width=stroke_width, show_grid=show_grid)

    if shape == "rectangle":
        w = float((spec.width or 8.0) * scale)
        h = float((spec.height or 3.0) * scale)
        hw, hh = w / 2, h / 2
        pts = [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]
        return _svg_wrap(_poly(pts), canvas_px=canvas_px, stroke_width=stroke_width, show_grid=show_grid)

    if shape == "triangle":
        s = float((spec.side or 6.0) * scale)
        h = (math.sqrt(3) / 2) * s
        pts = [(-s / 2, h / 3), (s / 2, h / 3), (0, -2 * h / 3)]
        return _svg_wrap(_poly(pts), canvas_px=canvas_px, stroke_width=stroke_width, show_grid=show_grid)

    if shape == "circle":
        r = float((spec.radius or 3.0) * scale)
        return _svg_wrap(f'<circle cx="0" cy="0" r="{r:.2f}" />',
                         canvas_px=canvas_px, stroke_width=stroke_width, show_grid=show_grid)

    if shape in ("regular_polygon", "polygon"):
        n = int(spec.n_sides or 6)
        if n < 3:
            raise ValueError("regular_polygon requires n_sides >= 3")

        R = float((spec.radius or 3.0) * scale)
        pts = []
        for k in range(n):
            ang = (2 * math.pi * k / n) - math.pi / 2
            pts.append((R * math.cos(ang), R * math.sin(ang)))
        return _svg_wrap(_poly(pts), canvas_px=canvas_px, stroke_width=stroke_width, show_grid=show_grid)

    raise ValueError(f"Unsupported shape '{shape}'. Try: circle, square, rectangle, triangle, hexagon, pentagon, regular polygon n=7 radius 2")
