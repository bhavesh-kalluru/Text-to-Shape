import json
import re


def premium_css() -> str:
    return """
<style>
/* subtle app-wide polish */
.block-container { padding-top: 1.2rem; padding-bottom: 2rem; }
h1, h2, h3 { letter-spacing: -0.02em; }
div[data-testid="stSidebarContent"] { padding-top: 1rem; }
.stTabs [data-baseweb="tab-list"] { gap: 6px; }
.stTabs [data-baseweb="tab"] {
  border-radius: 12px;
  padding: 10px 14px;
}
</style>
"""


def safe_json_like_shape_parse(text: str) -> dict:
    """
    Very small parser so typed input like "square" or "triangle" works without AI.
    Also supports JSON-ish: {"shape":"triangle","side":3}
    """
    t = (text or "").strip()
    if not t:
        return {}

    # If user pastes JSON, accept it
    if t.startswith("{") and t.endswith("}"):
        try:
            return json.loads(t)
        except Exception:
            return {}

    # Else: pull first word as shape token
    # e.g. "triangle with side 3" -> shape=triangle
    m = re.match(r"([a-zA-Z_]+)", t)
    if not m:
        return {}
    return {"shape": m.group(1).lower()}
