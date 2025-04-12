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

# Get available languages
available_languages = get_languages()

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

# App header with logo
col1, col2 = st.columns([1, 5])
with col1:
    st.markdown(f"""
        <div style='display: flex; justify-content: center; align-items: center; height: 100%;'>
            {logo_svg}
        </div>
    """, unsafe_allow_html=True)
with col2:
    st.title("Traductor Multilingüe")
    st.markdown("##### Traduce texto entre múltiples idiomas en tiempo real")

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

# Main translation interface
col1, col2, col3 = st.columns([2, 1, 2])

# Definir los idiomas más comunes
common_languages = ['en', 'es', 'fr', 'de', 'it', 'pt', 'zh-CN', 'ja', 'ko', 'ru', 'ar', 'hi']

# Source language selection
with col1:
    # Mostrar solo idiomas comunes (sin opción 'auto')
    source_options = [lang for lang in common_languages if lang in available_languages]
    
    # Determinar el índice actual
    current_source_index = 0
    if st.session_state.source_language in source_options:
        current_source_index = source_options.index(st.session_state.source_language)
    elif st.session_state.source_language != 'auto':
        # Si el idioma actual no está en las opciones comunes, agregarlo
        source_options.append(st.session_state.source_language)
        current_source_index = len(source_options) - 1
        
    source_language = st.selectbox(
        "Idioma de origen",
        source_options,
        format_func=lambda x: LANGUAGE_NAMES.get(x, x),
        index=current_source_index
    )
    st.session_state.source_language = source_language

# Swap languages button
with col2:
    st.write("")
    st.write("")
    if st.button("🔄 Intercambiar", use_container_width=True):
        # Only swap if not using auto-detect
        if st.session_state.source_language != 'auto':
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
    # Mostrar solo idiomas comunes
    target_options = [lang for lang in common_languages if lang in available_languages]
    
    # Asegurarse de que el idioma actual esté en las opciones
    if st.session_state.target_language not in target_options:
        target_options.append(st.session_state.target_language)
    
    # Determinar el índice actual
    default_index = 0
    if st.session_state.target_language in target_options:
        default_index = target_options.index(st.session_state.target_language)
       
    target_language = st.selectbox(
        "Idioma de destino",
        target_options,
        format_func=lambda x: LANGUAGE_NAMES.get(x, x),
        index=default_index
    )
    
    # Update session state when target language changes
    if st.session_state.target_language != target_language:
        st.session_state.target_language = target_language
        # Translate text with new target language if text exists
        if st.session_state.input_text:
            st.rerun()

# Text input area
st.subheader("Escribe texto para traducir")

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

# Input text area with callback
input_text = st.text_area(
    "Texto Original",
    value=st.session_state.input_text,
    height=150,
    placeholder="Escribe o pega texto aquí...",
    label_visibility="collapsed",
    key="text_input",
    on_change=handle_text_change
)

# Clear button
col1, col2 = st.columns([6, 1])
with col2:
    if st.button("Borrar", use_container_width=True):
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

# Translation output area
st.subheader("Traducción")
st.text_area(
    "Texto Traducido",
    value=st.session_state.translated_text,
    height=150,
    placeholder="La traducción aparecerá aquí...",
    label_visibility="collapsed",
    key="output_text_area",
    disabled=True
)

# Action buttons for the translated text
if st.session_state.translated_text:
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📋 Copiar", use_container_width=True):
            st.toast("¡Traducción copiada al portapapeles!")
            st.write(f'<p id="translated-text" style="position: absolute; top: -9999px;">{st.session_state.translated_text}</p>', unsafe_allow_html=True)
            st.write("""
            <script>
                const text = document.getElementById('translated-text').innerText;
                navigator.clipboard.writeText(text);
            </script>
            """, unsafe_allow_html=True)
    
    with col2:
        if st.button("🔊 Escuchar", use_container_width=True):
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
