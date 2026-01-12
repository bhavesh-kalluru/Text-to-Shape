import streamlit as st
import streamlit.components.v1 as components

from config import Settings
from shapes import draw_shape_outline_svg
from shape_parser import parse_shape_prompt
from utils import premium_css

st.set_page_config(page_title="Chat-to-Shape Sketch", page_icon="📐", layout="wide")
st.markdown(premium_css(), unsafe_allow_html=True)

settings = Settings.load()

st.title("📐 Chat-to-Shape Sketch (BIG)")
st.caption('Type: "Draw a rectangle 8 by 3", "Make a circle radius 4", "Create a hexagon radius 2"')

with st.sidebar:
    st.header("Appearance (Big Shapes)")

    prefer_ai_parse = st.toggle("Use OpenAI to parse prompts", value=True)
    st.caption("If OFF (or no OPENAI_API_KEY), rule-based parsing is used.")

    canvas_px = st.slider("Canvas height (px)", 600, 1400, 1000, 50)
    fill_ratio = st.slider("Fill ratio (how big the shape is)", 0.30, 0.95, 0.80, 0.05)
    stroke_width = st.slider("Stroke width", 4, 18, 10, 1)
    show_grid = st.toggle("Show grid background", value=False)

if "chat" not in st.session_state:
    st.session_state.chat = []

# Show chat history
for msg in st.session_state.chat:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant" and msg.get("svg"):
            components.html(msg["svg"], height=msg.get("height", 1050), scrolling=False)
            st.code(msg["spec_json"], language="json")
        else:
            st.write(msg["content"])

prompt = st.chat_input('Try: "Draw a pentagon radius 2" or "Create a 7-gon radius 3"')
if prompt:
    st.session_state.chat.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        try:
            spec = parse_shape_prompt(prompt, settings=settings, prefer_ai=prefer_ai_parse)

            svg = draw_shape_outline_svg(
                spec,
                canvas_px=canvas_px,
                fill_ratio=fill_ratio,
                stroke_width=stroke_width,
                show_grid=show_grid,
            )

            spec_json = spec.model_dump_json(indent=2)

            # Render BIG
            components.html(svg, height=canvas_px + 80, scrolling=False)
            st.code(spec_json, language="json")

            st.session_state.chat.append({
                "role": "assistant",
                "content": "Here’s the shape I generated.",
                "svg": svg,
                "spec_json": spec_json,
                "height": canvas_px + 80
            })

        except Exception as e:
            err = f"I couldn't generate that shape. Error: {e}"
            st.error(err)
            st.session_state.chat.append({"role": "assistant", "content": err})
