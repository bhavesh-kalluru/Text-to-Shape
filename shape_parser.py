import json
import re
from typing import Any, Optional

from openai import OpenAI

from config import Settings
from shapes import ShapeSpec

_VERBS = {"draw", "create", "make", "generate", "sketch", "render", "build", "show"}


def _strip_fences(s: str) -> str:
    s = s.strip()
    if s.startswith("```"):
        s = re.sub(r"^```[a-zA-Z]*", "", s).strip()
        s = s.rstrip("`").strip()
    return s


def _safe_json_loads(s: str) -> Optional[dict[str, Any]]:
    try:
        return json.loads(_strip_fences(s))
    except Exception:
        return None


def _clean_prompt(prompt: str) -> str:
    p = (prompt or "").strip().lower()
    p = re.sub(r"[,:;]", " ", p)
    tokens = p.split()
    while tokens and tokens[0] in _VERBS:
        tokens = tokens[1:]
    return " ".join(tokens)


def rule_based_parse(prompt: str) -> ShapeSpec:
    p = _clean_prompt(prompt)

    polygon_words = {
        "triangle": 3,
        "pentagon": 5,
        "hexagon": 6,
        "heptagon": 7,
        "octagon": 8,
        "nonagon": 9,
        "decagon": 10,
        "hendecagon": 11,
        "dodecagon": 12,
    }

    shape = None
    n_sides = None

    if any(w in p for w in ["circle", "round"]):
        shape = "circle"

    if shape is None:
        for s in ["square", "rectangle", "triangle"]:
            if s in p:
                shape = s
                break

    if shape is None:
        for w, n in polygon_words.items():
            if w in p:
                shape = "regular_polygon"
                n_sides = n
                break

    if shape is None:
        m = re.search(r"\b(\d+)\s*[- ]?gon\b", p)  # "7-gon"
        if m:
            shape = "regular_polygon"
            n_sides = int(m.group(1))

    if shape is None and ("polygon" in p):
        shape = "regular_polygon"

    if shape is None:
        shape = "square"

    nums = [float(x) for x in re.findall(r"(\d+(?:\.\d+)?)", p)]

    side = width = height = radius = None

    n_match = re.search(r"\bn\s*=\s*(\d+)\b", p)
    if n_match:
        n_sides = int(n_match.group(1))

    by_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:x|by)\s*(\d+(?:\.\d+)?)", p)
    if by_match:
        width = float(by_match.group(1))
        height = float(by_match.group(2))

    r_match = re.search(r"\bradius\s*=?\s*(\d+(?:\.\d+)?)\b", p)
    if r_match:
        radius = float(r_match.group(1))

    side_match = re.search(r"\bside\s*=?\s*(\d+(?:\.\d+)?)\b", p)
    if side_match:
        side = float(side_match.group(1))

    if shape in ("square", "triangle"):
        if side is None and nums:
            side = nums[0]

    if shape == "circle":
        if radius is None and nums:
            radius = nums[0]

    if shape == "rectangle":
        if width is None and height is None and len(nums) >= 2:
            width, height = nums[0], nums[1]

    if shape == "regular_polygon":
        if n_sides is None:
            sm = re.search(r"\b(\d+)\s*sides?\b", p)
            n_sides = int(sm.group(1)) if sm else 6
        if radius is None and nums:
            radius = nums[0]

    return ShapeSpec(shape=shape, side=side, width=width, height=height, radius=radius, n_sides=n_sides)


def ai_parse(prompt: str, settings: Settings) -> Optional[ShapeSpec]:
    if not settings.openai_api_key:
        return None

    client = OpenAI(api_key=settings.openai_api_key)

    system = """
Return ONLY valid JSON:
{
  "shape": "square|rectangle|triangle|circle|regular_polygon",
  "side": number|null,
  "width": number|null,
  "height": number|null,
  "radius": number|null,
  "n_sides": integer|null
}
Map pentagon/hexagon/etc => regular_polygon with correct n_sides.
If dimensions missing, use null (do not guess).
""".strip()

    resp = client.responses.create(
        model=settings.openai_model,
        input=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
    )

    data = _safe_json_loads(resp.output_text)
    if not data:
        return None

    try:
        return ShapeSpec(**data)
    except Exception:
        return None


def parse_shape_prompt(prompt: str, settings: Settings, prefer_ai: bool = True) -> ShapeSpec:
    if prefer_ai:
        spec = ai_parse(prompt, settings)
        if spec:
            return spec
    return rule_based_parse(prompt)
