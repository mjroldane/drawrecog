import os
import streamlit as st
import base64
import openai
from openai import OpenAI
from PIL import Image
import numpy as np

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title='Tablero Inteligente AI', layout="wide")

# Estilo CSS para mejorar la estética de los botones y el contenedor
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 4px;
        height: 3em;
        background-color: #4CAF50;
        color: white;
    }
    .result-box {
        padding: 20px;
        background-color: #262730;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
    }
    </style>
    """, unsafe_allow_html=True)

def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except FileNotFoundError:
        return None

# --- SIDEBAR ---
with st.sidebar:
    st.title("Configuración")
    st.markdown("Esta aplicación utiliza visión artificial para interpretar bocetos en tiempo real.")
    
    st.markdown("---")
    stroke_width = st.slider('Grosor del trazo', 1, 30, 5)
    
    # Selector de clave más profesional
    ke = st.text_input('OpenAI API Key', type="password", help="Ingresa tu clave de OpenAI para activar el análisis")
    os.environ['OPENAI_API_KEY'] = ke

# --- DISEÑO PRINCIPAL ---
st.title("Tablero Inteligente")
st.write("Dibuja tu idea y deja que la inteligencia artificial la describa.")

col_main, col_res = st.columns([2, 1])

with col_main:
    from streamlit_drawable_canvas import st_canvas
    
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=stroke_width,
        stroke_color="#000000",
        background_color="#FFFFFF",
        height=400,
        width=600,
        drawing_mode="freedraw",
        key="canvas",
    )
    
    analyze_button = st.button("Analizar Boceto", type="primary")

with col_res:
    # Este es el panel que "entra y sale" (Expander)
    with st.expander("Panel de Resultados", expanded=True):
        if not ke:
            st.warning("Falta la API Key en el menú lateral.")
        
        message_placeholder = st.empty()
        
        if canvas_result.image_data is not None and ke and analyze_button:
            with st.spinner("Analizando trazos..."):
                try:
                    # Procesamiento de imagen
                    input_numpy_array = np.array(canvas_result.image_data)
                    input_image = Image.fromarray(input_numpy_array.astype('uint8'), 'RGBA')
                    input_image.save('img.png')
                    
                    base64_image = encode_image_to_base64("img.png")
                    prompt_text = "Describe en español de manera breve y profesional qué representa este boceto."
                    
                    # Cliente OpenAI
                    client = OpenAI(api_key=ke)
                    
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": prompt_text},
                                    {
                                        "type": "image_url",
                                        "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                                    },
                                ],
                            }
                        ],
                        max_tokens=300,
                    )
                    
                    # Mostrar respuesta
                    full_response = response.choices[0].message.content
                    message_placeholder.markdown(f"""
                        <div class='result-box'>
                            {full_response}
                        </div>
                        """, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"Error técnico: {e}")
        else:
            st.info("El análisis aparecerá aquí después de dibujar.")

st.markdown("---")
st.caption("Tecnología GPT-4o-mini Vision")
