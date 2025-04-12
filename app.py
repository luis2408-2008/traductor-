import streamlit as st
from deep_translator import GoogleTranslator
from translator import get_languages, translate_text, detect_language
from tts import text_to_speech
from utils import LANGUAGE_NAMES
import base64
from tempfile import NamedTemporaryFile
import os

# App configuration
st.set_page_config(
    page_title="Traductor Multilingüe",
    page_icon="🌐",
    layout="wide"
)

# CSS avanzado para un diseño impresionante
st.markdown("""
<style>
    /* Estilo general y fuentes */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Fondo con degradado */
    .main {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
    }
    
    /* Contenedores con efecto de cristal (glassmorphism) */
    .block-container {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Selectores de idioma */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 15px;
        color: white;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .stSelectbox > div {
        color: white;
    }
    
    /* Áreas de texto */
    .stTextArea > div > div {
        background: rgba(255, 255, 255, 0.15);
        border: 2px solid rgba(255, 255, 255, 0.3);
        border-radius: 15px;
        color: white;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(5px);
        transition: all 0.3s ease;
    }
    
    .stTextArea > div > div:focus-within {
        border-color: #64B5F6;
        box-shadow: 0 0 0 2px #64B5F6;
    }
    
    /* Botones con degradado y animación */
    .stButton > button {
        background: linear-gradient(135deg, #4A91F2 0%, #67B26F 100%);
        border-radius: 12px;
        border: none;
        color: white;
        font-weight: 600;
        padding: 0.6rem 1.2rem;
        transition: all 0.3s ease;
        transform: translateY(0);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #67B26F 0%, #4A91F2 100%);
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Encabezados con efecto de texto */
    h1, h2, h3 {
        background: linear-gradient(90deg, #ffffff, #f0f0f0);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        font-weight: 700;
        letter-spacing: 1px;
        text-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    }
    
    h1 {
        font-size: 2.5rem;
    }
    
    /* Efecto de destello para los botones */
    @keyframes shine {
        0% {
            background-position: 0% 50%;
        }
        50% {
            background-position: 100% 50%;
        }
        100% {
            background-position: 0% 50%;
        }
    }
    
    /* Mensaje de éxito */
    .stSuccess {
        background: rgba(102, 187, 106, 0.3);
        backdrop-filter: blur(5px);
        border-radius: 10px;
        border: 1px solid #66BB6A;
        color: white;
    }
    
    /* Mensaje de error */
    .stError {
        background: rgba(244, 67, 54, 0.3);
        backdrop-filter: blur(5px);
        border-radius: 10px;
        border: 1px solid #F44336;
        color: white;
    }
    
    /* Mensaje de información */
    .stInfo {
        background: rgba(100, 181, 246, 0.3);
        backdrop-filter: blur(5px);
        border-radius: 10px;
        border: 1px solid #64B5F6;
        color: white;
    }
    
    /* Botón de intercambiar con animación */
    .swap-btn {
        background: rgba(255, 255, 255, 0.15);
        border-radius: 50%;
        width: 50px;
        height: 50px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.3s ease;
        margin: 0 auto;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .swap-btn:hover {
        background: rgba(255, 255, 255, 0.25);
        transform: rotate(180deg);
    }
    
    /* Sidebar personalizada */
    .css-1d391kg, .css-12oz5g7 {
        background: linear-gradient(180deg, #1e3c72 0%, #2c3e50 100%);
    }
    
    /* Título del sidebar */
    .css-1d391kg h1, .css-12oz5g7 h1 {
        color: white;
    }
    
    /* Radio buttons */
    .stRadio > div {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 10px;
    }
    
    /* Separador */
    hr {
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
        border: none;
        margin: 1.5rem 0;
    }
    
    /* Efectos de partículas flotantes */
    @keyframes float {
        0% {
            transform: translateY(0px) rotate(0deg);
        }
        50% {
            transform: translateY(-20px) rotate(10deg);
        }
        100% {
            transform: translateY(0px) rotate(0deg);
        }
    }
    
    .particle {
        position: absolute;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 50%;
        pointer-events: none;
        animation: float 8s infinite ease-in-out;
    }
    
    /* Contenedor de audio */
    audio {
        width: 100%;
        border-radius: 10px;
        background: rgba(255, 255, 255, 0.1);
    }
    
    /* Ajustes para móviles */
    @media (max-width: 768px) {
        .main {
            padding: 1rem;
        }
        
        h1 {
            font-size: 1.8rem;
        }
    }
</style>

<!-- Partículas decorativas para efecto visual -->
<div class="particle" style="width: 100px; height: 100px; top: 10%; left: 5%; opacity: 0.2; animation-delay: 0s;"></div>
<div class="particle" style="width: 150px; height: 150px; top: 30%; left: 80%; opacity: 0.1; animation-delay: 2s;"></div>
<div class="particle" style="width: 50px; height: 50px; top: 70%; left: 15%; opacity: 0.15; animation-delay: 4s;"></div>
<div class="particle" style="width: 80px; height: 80px; top: 50%; left: 60%; opacity: 0.1; animation-delay: 6s;"></div>
""", unsafe_allow_html=True)

# Get available languages
available_languages = get_languages()

# Function to translate text and update session
def translate_and_update():
    try:
        # Auto-detect if source is 'auto'
        if st.session_state.source_language == 'auto':
            detected = detect_language(st.session_state.input_text)
            # Make sure the detected language is in the available languages
            st.session_state.detected_language = detected if detected in available_languages else 'en'
            source_lang = st.session_state.detected_language
        else:
            source_lang = st.session_state.source_language
            st.session_state.detected_language = source_lang
        
        # Get translation
        st.session_state.translated_text = translate_text(
            st.session_state.input_text, 
            source_lang, 
            st.session_state.target_language
        )
        
        # Add to history if it's a meaningful translation
        if st.session_state.translated_text and st.session_state.translated_text != st.session_state.input_text:
            history_entry = (
                st.session_state.detected_language if st.session_state.source_language == 'auto' else st.session_state.source_language,
                st.session_state.target_language, 
                st.session_state.input_text, 
                st.session_state.translated_text
            )
            if history_entry not in st.session_state.history:
                st.session_state.history.append(history_entry)
                # Keep only the last 10 translations
                if len(st.session_state.history) > 10:
                    st.session_state.history.pop(0)
    except Exception as e:
        st.error(f"Error de traducción: {str(e)}")
        st.session_state.translated_text = ""

# Text input callback - to be used when text changes
def handle_text_change():
    text = st.session_state.text_input
    if text != st.session_state.input_text:
        st.session_state.input_text = text
        # Translate only if there's text to translate
        if text:
            translate_and_update()
        else:
            st.session_state.translated_text = ""

# Initialize session state variables if they don't exist
if 'source_language' not in st.session_state:
    # Set to Spanish as default if available, otherwise first language
    if 'es' in available_languages:
        st.session_state.source_language = 'es'
    else:
        # Use first available language as default
        st.session_state.source_language = list(available_languages.keys())[0]
        
if 'target_language' not in st.session_state:
    # Set initial target language to English if available
    if 'en' in available_languages:
        st.session_state.target_language = 'en'
    else:
        # Use first available language as default
        st.session_state.target_language = list(available_languages.keys())[0]
if 'input_text' not in st.session_state:
    st.session_state.input_text = ''
if 'translated_text' not in st.session_state:
    st.session_state.translated_text = ''
if 'detected_language' not in st.session_state:
    st.session_state.detected_language = ''
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'
if 'history' not in st.session_state:
    st.session_state.history = []

# Logo SVG
with open('assets/logo.svg', 'r') as f:
    logo_svg = f.read()

# App header with glassmorphism effect
st.markdown("""
<div style="background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); border-radius: 20px; 
    padding: 1.5rem; margin-bottom: 2rem; border: 1px solid rgba(255, 255, 255, 0.2); text-align: center; 
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);">
    <h1 style="font-size: 3rem; margin-bottom: 0.5rem; background: linear-gradient(90deg, #64B5F6, #9575CD);
        -webkit-background-clip: text; background-clip: text; color: transparent; font-weight: 700;">
        Traductor Multilingüe</h1>
    <p style="font-size: 1.2rem; opacity: 0.8; margin-top: 0;">Traduce texto entre múltiples idiomas en tiempo real</p>
</div>
""", unsafe_allow_html=True)

# Theme switcher in the sidebar
with st.sidebar:
    st.title("Configuración")
    theme = st.radio("Tema", ["Claro", "Oscuro"], 
                     index=0 if st.session_state.theme == 'light' else 1,
                     horizontal=True)
    st.session_state.theme = 'light' if theme == "Claro" else 'dark'
    
    st.markdown("---")
    st.subheader("Traducciones Recientes")
    
    # Display history
    if st.session_state.history:
        for i, (src, tgt, txt, trans) in enumerate(st.session_state.history[-5:]):
            with st.expander(f"{LANGUAGE_NAMES.get(src, 'Auto')} → {LANGUAGE_NAMES.get(tgt, 'Desconocido')}", expanded=False):
                st.write(f"**Original:** {txt[:50]}{'...' if len(txt) > 50 else ''}")
                st.write(f"**Traducción:** {trans[:50]}{'...' if len(trans) > 50 else ''}")
    else:
        st.write("No hay traducciones recientes")

# Main translation interface - Container with glass effect
with st.container():
    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.05); 
                backdrop-filter: blur(5px); 
                border-radius: 16px; 
                padding: 20px; 
                margin-bottom: 20px;
                border: 1px solid rgba(255, 255, 255, 0.15);
                box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);">
    </div>
    """, unsafe_allow_html=True)
    
    # Language selection headers
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col1:
        st.markdown("""
        <h4 style="margin-bottom: 5px; color: rgba(255, 255, 255, 0.8); text-align: center;">
            Idioma de Origen
        </h4>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <h4 style="margin-bottom: 5px; color: rgba(255, 255, 255, 0.8); text-align: center;">
            Idioma de Destino
        </h4>
        """, unsafe_allow_html=True)
    
    # Language selectors and swap button
    col1, col2, col3 = st.columns([2, 1, 2])
    
    # Source language selection
    with col1:
        source_language = st.selectbox(
            "",
            options=list(available_languages.keys()),
            format_func=lambda x: LANGUAGE_NAMES.get(x, x),
            index=list(available_languages.keys()).index(st.session_state.source_language) if st.session_state.source_language in available_languages else 0,
            label_visibility="collapsed",
            key="source_language_select"
        )
        if st.session_state.source_language != source_language:
            st.session_state.source_language = source_language
            if st.session_state.input_text:
                translate_and_update()
    
    # Swap languages button with custom styling
    with col2:
        st.markdown("""
        <div style="display: flex; justify-content: center; align-items: center; height: 100%;">
            <div id="swap-btn" class="swap-btn" onclick="swapLanguages()">
                <span style="font-size: 24px; color: white;">🔄</span>
            </div>
        </div>
        
        <script>
        function swapLanguages() {
            // Este es un botón visual, la funcionalidad real está en el botón de Streamlit oculto
            document.getElementById('swap-languages-btn').click();
        }
        </script>
        """, unsafe_allow_html=True)
        
        # Botón real de Streamlit pero con estilo invisible
        if st.button("", key="swap-languages-btn"):
            temp_source = st.session_state.source_language
            temp_target = st.session_state.target_language
            st.session_state.source_language = temp_target
            st.session_state.target_language = temp_source
            
            # Update translation with swapped languages
            if st.session_state.input_text:
                # Force a rerun to update the UI 
                st.rerun()
    
    # Target language selection
    with col3:
        target_language = st.selectbox(
            "",
            options=list(available_languages.keys()),
            format_func=lambda x: LANGUAGE_NAMES.get(x, x),
            index=list(available_languages.keys()).index(st.session_state.target_language) if st.session_state.target_language in available_languages else 0,
            label_visibility="collapsed",
            key="target_language_select"
        )
        
        # Update session state when target language changes
        if st.session_state.target_language != target_language:
            st.session_state.target_language = target_language
            # Translate text with new target language if text exists
            if st.session_state.input_text:
                translate_and_update()

# Function to translate text and update session
def translate_and_update():
    try:
        # Auto-detect if source is 'auto'
        if st.session_state.source_language == 'auto':
            detected = detect_language(st.session_state.input_text)
            # Make sure the detected language is in the available languages
            st.session_state.detected_language = detected if detected in available_languages else 'en'
            source_lang = st.session_state.detected_language
        else:
            source_lang = st.session_state.source_language
            st.session_state.detected_language = source_lang
        
        # Get translation
        st.session_state.translated_text = translate_text(
            st.session_state.input_text, 
            source_lang, 
            st.session_state.target_language
        )
        
        # Add to history if it's a meaningful translation
        if st.session_state.translated_text and st.session_state.translated_text != st.session_state.input_text:
            history_entry = (
                st.session_state.detected_language if st.session_state.source_language == 'auto' else st.session_state.source_language,
                st.session_state.target_language, 
                st.session_state.input_text, 
                st.session_state.translated_text
            )
            if history_entry not in st.session_state.history:
                st.session_state.history.append(history_entry)
                # Keep only the last 10 translations
                if len(st.session_state.history) > 10:
                    st.session_state.history.pop(0)
    except Exception as e:
        st.error(f"Error de traducción: {str(e)}")
        st.session_state.translated_text = ""

# Text input callback - to be used when text changes
def handle_text_change():
    text = st.session_state.text_input
    if text != st.session_state.input_text:
        st.session_state.input_text = text
        # Translate only if there's text to translate
        if text:
            translate_and_update()
        else:
            st.session_state.translated_text = ""

# Main container for text areas with glassmorphism effect
st.markdown("""
<div style="
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(5px);
    border-radius: 16px;
    padding: 20px;
    margin: 20px 0;
    border: 1px solid rgba(255, 255, 255, 0.15);
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);">
</div>
""", unsafe_allow_html=True)

# Text input side - with animated header
st.markdown("""
<h3 style="color: white; font-weight: 600; margin-bottom: 10px; text-align: center;">
    <span style="background: linear-gradient(90deg, #64B5F6, #9575CD);
                -webkit-background-clip: text;
                background-clip: text;
                color: transparent;
                animation: shine 3s infinite linear;">
        ✍️ Escribe texto para traducir
    </span>
</h3>
""", unsafe_allow_html=True)

# Input text area with callback
input_text = st.text_area(
    "Texto Original",
    value=st.session_state.input_text,
    height=180,
    placeholder="Escribe o pega texto aquí...",
    label_visibility="collapsed",
    key="text_input",
    on_change=handle_text_change
)

# Text character count and clear button in a horizontal layout
col1, col2 = st.columns([4, 1])

with col1:
    if st.session_state.input_text:
        char_count = len(st.session_state.input_text)
        st.markdown(f"""
        <p style="color: rgba(255, 255, 255, 0.7); font-size: 0.9rem; margin-bottom: 15px;">
            {char_count} caracteres
        </p>
        """, unsafe_allow_html=True)

with col2:
    if st.button("🗑️ Borrar", use_container_width=True, type="secondary", key="clear_button"):
        st.session_state.input_text = ""
        # No podemos modificar text_input directamente después de que se haya creado el widget
        # En su lugar, limpiaremos el texto y recargaremos la página
        st.session_state.translated_text = ""
        st.rerun()

# Translate if text exists but translated_text is empty
if st.session_state.input_text and not st.session_state.translated_text:
    translate_and_update()

# Show detected language if using auto-detect
if st.session_state.source_language == 'auto' and st.session_state.detected_language:
    st.info(f"Idioma detectado: {LANGUAGE_NAMES.get(st.session_state.detected_language, st.session_state.detected_language)}")

# Translation output with animated header
st.markdown("""
<h3 style="color: white; font-weight: 600; margin: 20px 0 10px 0; text-align: center;">
    <span style="background: linear-gradient(90deg, #9575CD, #64B5F6);
                -webkit-background-clip: text;
                background-clip: text;
                color: transparent;
                animation: shine 3s infinite linear;">
        🔄 Traducción
    </span>
</h3>
""", unsafe_allow_html=True)

# Custom container for translated text with subtle animation
if st.session_state.translated_text:
    st.markdown(f"""
    <div style="
        background: rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 10px;
        border: 1px solid rgba(100, 181, 246, 0.3);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        color: white;
        font-size: 1.1rem;
        line-height: 1.6;
        min-height: 180px;
        animation: fadeIn 0.5s ease-in-out;
        overflow-y: auto;
        word-wrap: break-word;">
        {st.session_state.translated_text}
    </div>
    
    <style>
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    </style>
    """, unsafe_allow_html=True)
else:
    # Placeholder cuando no hay texto traducido
    st.markdown("""
    <div style="
        background: rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        color: rgba(255, 255, 255, 0.5);
        font-size: 1.1rem;
        min-height: 180px;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;">
        <p>La traducción aparecerá aquí mientras escribes...</p>
    </div>
    """, unsafe_allow_html=True)

# Action buttons for the translated text
if st.session_state.translated_text:
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📋 Copiar", use_container_width=True, key="copy_button"):
            st.toast("¡Traducción copiada al portapapeles!")
            st.write(f'<p id="translated-text" style="position: absolute; top: -9999px;">{st.session_state.translated_text}</p>', unsafe_allow_html=True)
            st.write("""
            <script>
                const text = document.getElementById('translated-text').innerText;
                navigator.clipboard.writeText(text);
            </script>
            """, unsafe_allow_html=True)
    
    with col2:
        if st.button("🔊 Escuchar", use_container_width=True, key="listen_button"):
            try:
                with st.spinner("Generando audio..."):
                    audio_file = text_to_speech(
                        st.session_state.translated_text,
                        st.session_state.target_language
                    )
                    
                    # Get audio file content
                    audio_bytes = audio_file.getvalue()
                    
                    # Play the audio
                    st.audio(audio_bytes, format='audio/mp3')
                    st.success("¡Audio generado correctamente!")
            except Exception as e:
                st.error(f"Error al generar audio: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center;'>
        <p>Desarrollado con deep-translator y Streamlit | 2023</p>
    </div>
    """,
    unsafe_allow_html=True
)
