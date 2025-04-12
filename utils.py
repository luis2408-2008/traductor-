import streamlit as st
from translator import translate_text, detect_language
import json

# Language names mapping - Spanish translations
LANGUAGE_NAMES = {
    'af': 'Afrikáans',
    'ar': 'Árabe',
    'bg': 'Búlgaro',
    'bn': 'Bengalí',
    'bs': 'Bosnio',
    'ca': 'Catalán',
    'cs': 'Checo',
    'cy': 'Galés',
    'da': 'Danés',
    'de': 'Alemán',
    'el': 'Griego',
    'en': 'Inglés',
    'eo': 'Esperanto',
    'es': 'Español',
    'et': 'Estonio',
    'fa': 'Persa',
    'fi': 'Finlandés',
    'fr': 'Francés',
    'ga': 'Irlandés',
    'gu': 'Gujarati',
    'he': 'Hebreo',
    'hi': 'Hindi',
    'hr': 'Croata',
    'ht': 'Haitiano',
    'hu': 'Húngaro',
    'id': 'Indonesio',
    'is': 'Islandés',
    'it': 'Italiano',
    'ja': 'Japonés',
    'jw': 'Javanés',
    'km': 'Jemer',
    'kn': 'Canarés',
    'ko': 'Coreano',
    'la': 'Latín',
    'lv': 'Letón',
    'ml': 'Malayalam',
    'mr': 'Marathi',
    'ms': 'Malayo',
    'my': 'Birmano',
    'ne': 'Nepalí',
    'nl': 'Holandés',
    'no': 'Noruego',
    'pa': 'Punyabí',
    'pl': 'Polaco',
    'pt': 'Portugués',
    'ro': 'Rumano',
    'ru': 'Ruso',
    'si': 'Cingalés',
    'sk': 'Eslovaco',
    'sq': 'Albanés',
    'sr': 'Serbio',
    'su': 'Sundanés',
    'sv': 'Sueco',
    'sw': 'Swahili',
    'ta': 'Tamil',
    'te': 'Telugu',
    'th': 'Tailandés',
    'tl': 'Filipino',
    'tr': 'Turco',
    'uk': 'Ucraniano',
    'ur': 'Urdu',
    'vi': 'Vietnamita',
    'zh-CN': 'Chino (Simplificado)',
    'zh-TW': 'Chino (Tradicional)',
    'auto': 'Detección automática'
}

def update_translation():
    """Update the translation based on current session state"""
    if st.session_state.input_text:
        try:
            # Auto-detect if source is 'auto'
            if st.session_state.source_language == 'auto':
                detected = detect_language(st.session_state.input_text)
                st.session_state.detected_language = detected
                source_lang = detected
            else:
                source_lang = st.session_state.source_language
                st.session_state.detected_language = source_lang
            
            # Get translation
            st.session_state.translated_text = translate_text(
                st.session_state.input_text, 
                source_lang, 
                st.session_state.target_language
            )
        except Exception as e:
            st.error(f"Translation error: {str(e)}")
            st.session_state.translated_text = ""
    else:
        st.session_state.translated_text = ""
