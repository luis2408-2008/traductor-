import streamlit as st
from deep_translator import GoogleTranslator
from translator import get_languages, translate_text, detect_language
from tts import text_to_speech
from utils import LANGUAGE_NAMES, update_translation
import base64
from tempfile import NamedTemporaryFile
import os

# App configuration
st.set_page_config(
    page_title="MultiLingual Translator",
    page_icon="🌐",
    layout="wide"
)

# Get available languages
available_languages = get_languages()

# Initialize session state variables if they don't exist
if 'source_language' not in st.session_state:
    st.session_state.source_language = 'auto'
if 'target_language' not in st.session_state:
    # Set initial target language to first available language or 'en' if it exists
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
    st.title("MultiLingual Translator")
    st.markdown("##### Translate text between multiple languages in real-time")

# Theme switcher in the sidebar
with st.sidebar:
    st.title("Settings")
    theme = st.radio("Theme", ["Light", "Dark"], 
                     index=0 if st.session_state.theme == 'light' else 1,
                     horizontal=True)
    st.session_state.theme = 'light' if theme == "Light" else 'dark'
    
    st.markdown("---")
    st.subheader("Recent Translations")
    
    # Display history
    if st.session_state.history:
        for i, (src, tgt, txt, trans) in enumerate(st.session_state.history[-5:]):
            with st.expander(f"{LANGUAGE_NAMES.get(src, 'Auto')} → {LANGUAGE_NAMES.get(tgt, 'Unknown')}", expanded=False):
                st.write(f"**Original:** {txt[:50]}{'...' if len(txt) > 50 else ''}")
                st.write(f"**Translation:** {trans[:50]}{'...' if len(trans) > 50 else ''}")
    else:
        st.write("No recent translations")

# Main translation interface
col1, col2, col3 = st.columns([2, 1, 2])

# Source language selection
with col1:
    source_language = st.selectbox(
        "Source Language",
        ['auto'] + list(available_languages.keys()),
        format_func=lambda x: 'Auto Detect' if x == 'auto' else LANGUAGE_NAMES.get(x, x),
        index=0
    )
    st.session_state.source_language = source_language

# Swap languages button
with col2:
    st.write("")
    st.write("")
    if st.button("🔄 Swap", use_container_width=True):
        # Only swap if not using auto-detect
        if st.session_state.source_language != 'auto':
            st.session_state.source_language, st.session_state.target_language = st.session_state.target_language, st.session_state.source_language
            # Update the translation if there's input text
            if st.session_state.input_text:
                # Force a rerun to update the UI with the new translation
                st.rerun()

# Target language selection
with col3:
    # Check if target language is in available languages
    target_language_list = list(available_languages.keys())
    default_index = 0
    
    # Try to find the index of the session target language, use default if not found
    try:
        if st.session_state.target_language in target_language_list:
            default_index = target_language_list.index(st.session_state.target_language)
    except:
        # If there's any error, default to first language
        pass
        
    target_language = st.selectbox(
        "Target Language",
        target_language_list,
        format_func=lambda x: LANGUAGE_NAMES.get(x, x),
        index=default_index
    )
    st.session_state.target_language = target_language

# Text input area
st.subheader("Enter text to translate")

# This function updates the input text in session state and triggers translation
def update_input_text():
    # Update the input text in session state
    st.session_state.input_text = st.session_state.input_text_area
    
# Configure text input area with callback
input_text = st.text_area(
    "Original Text",
    value=st.session_state.input_text,
    height=150,
    placeholder="Type or paste text here...",
    label_visibility="collapsed",
    key="input_text_area",
    on_change=update_input_text
)

# Clear button
col1, col2 = st.columns([6, 1])
with col2:
    if st.button("Clear", use_container_width=True):
        st.session_state.input_text = ""
        st.session_state.translated_text = ""
        st.rerun()

# Process translation when input changes
if input_text and (input_text == st.session_state.input_text):
    # Call the update_translation utility function to handle translation
    update_translation()
    
    # Add to history if it's a meaningful translation
    if st.session_state.translated_text and st.session_state.translated_text != input_text:
        history_entry = (
            st.session_state.detected_language if st.session_state.source_language == 'auto' else st.session_state.source_language,
            st.session_state.target_language, 
            input_text, 
            st.session_state.translated_text
        )
        if history_entry not in st.session_state.history:
            st.session_state.history.append(history_entry)
            # Keep only the last 10 translations
            if len(st.session_state.history) > 10:
                st.session_state.history.pop(0)
elif not input_text:
    st.session_state.translated_text = ""

# Show detected language if using auto-detect
if st.session_state.source_language == 'auto' and st.session_state.detected_language:
    st.info(f"Detected language: {LANGUAGE_NAMES.get(st.session_state.detected_language, st.session_state.detected_language)}")

# Translation output area
st.subheader("Translation")
st.text_area(
    "Translated Text",
    value=st.session_state.translated_text,
    height=150,
    placeholder="Translation will appear here...",
    label_visibility="collapsed",
    key="output_text_area",
    disabled=True
)

# Action buttons for the translated text
if st.session_state.translated_text:
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📋 Copy to Clipboard", use_container_width=True):
            st.toast("Translation copied to clipboard!")
            st.write(f'<p id="translated-text" style="position: absolute; top: -9999px;">{st.session_state.translated_text}</p>', unsafe_allow_html=True)
            st.write("""
            <script>
                const text = document.getElementById('translated-text').innerText;
                navigator.clipboard.writeText(text);
            </script>
            """, unsafe_allow_html=True)
    
    with col2:
        if st.button("🔊 Text to Speech", use_container_width=True):
            try:
                with st.spinner("Generating audio..."):
                    audio_file = text_to_speech(
                        st.session_state.translated_text,
                        st.session_state.target_language
                    )
                    
                    # Get audio file content
                    audio_bytes = audio_file.getvalue()
                    
                    # Play the audio
                    st.audio(audio_bytes, format='audio/mp3')
                    st.success("Audio generated successfully!")
            except Exception as e:
                st.error(f"Error generating audio: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center;'>
        <p>Powered by deep-translator and Streamlit | 2023</p>
    </div>
    """,
    unsafe_allow_html=True
)
