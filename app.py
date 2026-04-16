import os
import streamlit as st
import base64
import numpy as np
import openai
from openai import OpenAI
from PIL import Image
from streamlit_drawable_canvas import st_canvas

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Tablero Inteligente AI", layout="wide")

# --- CSS PARA ESTÉTICA PREMIUM ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        color: white;
    }
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    div[data-testid="stExpander"], .result-box {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
    }
    .stButton>button {
        background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%);
        color: #000 !important;
        font-weight: bold;
        border-radius: 12px;
        border: none;
        height: 3em;
        width: 100%;
    }
    .stCanvas {
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    </style>
    """, unsafe_allow_html=True)

def encode_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

# --- SIDEBAR (Basado en tus imágenes) ---
with st.sidebar:
    st.header("Propiedades del Tablero")
    
    with st.expander("Dimensiones del Tablero", expanded=False):
        canvas_width = st.slider("Ancho del tablero", 300, 700, 500, 50)
        canvas_height = st.slider("Alto del tablero", 200, 600, 300, 50)

    drawing_mode = st.selectbox(
        "Herramienta de Dibujo:",
        ("freedraw", "line", "rect", "circle", "transform", "polygon", "point"),
    )

    stroke_width = st.slider('Selecciona el ancho de línea', 1, 30, 15)
    stroke_color = st.color_picker("Color de trazo", "#000000")
    bg_color = st.color_picker("Color de fondo", "#FFFFFF")
    
    st.markdown("---")
    api_key = st.text_input("OpenAI API Key", type="password")

# --- CUERPO PRINCIPAL ---
st.title("Tablero Inteligente")
st.markdown("##### Dibuja un boceto y deja que la IA lo analice")

col_canvas, col_info = st.columns([1.5, 1])

with col_canvas:
    # Canvas con los parámetros exactos de tu imagen
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color=bg_color,
        height=canvas_height,
        width=canvas_width,
        drawing_mode=drawing_mode,
        key=f"canvas_{canvas_width}_{canvas_height}",
    )
    
    c1, c2 = st.columns([2, 1])
    with c1:
        btn_analizar = st.button("ANALIZAR IMAGEN")
    with c2:
        if st.button("BORRAR TODO"):
            st.rerun()

with col_info:
    with st.expander("Análisis de la IA", expanded=True):
        if btn_analizar:
            if not api_key:
                st.warning("Ingresa la API Key en el menú lateral.")
            elif canvas_result.image_data is not None:
                with st.spinner("Analizando trazos..."):
                    try:
                        # Guardar imagen temporal
                        img_array = np.array(canvas_result.image_data)
                        img = Image.fromarray(img_array.astype('uint8'), 'RGBA')
                        img.save("boceto.png")
                        
                        b64_img = encode_image("boceto.png")
                        
                        # Cliente OpenAI
                        client = OpenAI(api_key=api_key)
                        response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[{
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": "Describe brevemente este dibujo en español."},
                                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64_img}"}}
                                ]
                            }]
                        )
                        st.markdown(f"<div class='result-box'>{response.choices[0].message.content}</div>", unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.info("El lienzo está vacío.")
        else:
            st.info("Esperando dibujo...")
