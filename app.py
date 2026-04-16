import os
import streamlit as st
import base64
from openai import OpenAI
from PIL import Image
import numpy as np

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title='AI Creative Board', layout="wide")

# --- CSS AVANZADO PARA ESTÉTICA PREMIUM ---
st.markdown("""
    <style>
    /* Fondo con degradado animado */
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

    /* Contenedores tipo 'Glassmorphism' */
    div[data-testid="stExpander"], .result-box {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
    }

    /* Estilo del botón principal */
    .stButton>button {
        background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%);
        color: #000 !important;
        font-weight: bold;
        border: none;
        border-radius: 20px;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0px 0px 15px rgba(146, 254, 157, 0.4);
    }

    /* Ajustes de texto */
    h1, h2, h3, p, span {
        color: #ffffff !important;
    }

    /* Quitar bordes feos del canvas */
    .stCanvas {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
    }
    </style>
    """, unsafe_allow_html=True)

def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except Exception:
        return None

# --- SIDEBAR ESTILIZADO ---
with st.sidebar:
    st.markdown("## Herramientas")
    with st.container():
        ke = st.text_input('OpenAI API Key', type="password")
        stroke_width = st.slider('Grosor del trazo', 1, 30, 6)
        st.info("Dibuja líneas claras para que la IA interprete mejor tu idea.")

# --- CUERPO PRINCIPAL ---
st.title("Tablero Inteligente")
st.markdown("##### Transforma tus bocetos en descripciones profesionales mediante IA")

col_left, col_right = st.columns([1.5, 1])

with col_left:
    from streamlit_drawable_canvas import st_canvas
    
    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0.1)",
        stroke_width=stroke_width,
        stroke_color="#000000",
        background_color="#FFFFFF", # Fondo blanco para que la IA vea mejor el contraste
        height=450,
        width=650,
        drawing_mode="freedraw",
        key="canvas",
    )
    
    if st.button("ANALIZAR BOCETO"):
        if not ke:
            st.error("Por favor, ingresa tu clave de OpenAI en el panel lateral.")
        else:
            process_trigger = True
    else:
        process_trigger = False

with col_right:
    st.markdown("### Análisis de la IA")
    
    # Contenedor de resultados "sacable"
    with st.expander("Resultados del procesamiento", expanded=True):
        res_placeholder = st.empty()
        
        if process_trigger and canvas_result.image_data is not None:
            with st.spinner("Procesando visión artificial..."):
                try:
                    # Guardar y codificar
                    input_array = np.array(canvas_result.image_data)
                    img = Image.fromarray(input_array.astype('uint8'), 'RGBA')
                    img.save('temp_boceto.png')
                    
                    base64_img = encode_image_to_base64('temp_boceto.png')
                    
                    client = OpenAI(api_key=ke)
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Describe brevemente y con lenguaje elegante qué ves en este dibujo."},
                                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_img}"}}
                            ]
                        }],
                        max_tokens=200
                    )
                    
                    res_text = response.choices[0].message.content
                    res_placeholder.markdown(f"<div class='result-box'>{res_text}</div>", unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            res_placeholder.write("Esperando un dibujo para analizar...")

st.markdown("<br><center><small>AI Creative Board v3.0 | Deep Vision Integration</small></center>", unsafe_allow_html=True)
