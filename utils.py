import streamlit as st
from translator import translate_text, detect_language
import json

# Language names mapping
LANGUAGE_NAMES = {
    'af': 'Afrikaans',
    'ar': 'Arabic',
    'bg': 'Bulgarian',
    'bn': 'Bengali',
    'bs': 'Bosnian',
    'ca': 'Catalan',
    'cs': 'Czech',
    'cy': 'Welsh',
    'da': 'Danish',
    'de': 'German',
    'el': 'Greek',
    'en': 'English',
    'eo': 'Esperanto',
    'es': 'Spanish',
    'et': 'Estonian',
    'fa': 'Persian',
    'fi': 'Finnish',
    'fr': 'French',
    'ga': 'Irish',
    'gu': 'Gujarati',
    'he': 'Hebrew',
    'hi': 'Hindi',
    'hr': 'Croatian',
    'ht': 'Haitian',
    'hu': 'Hungarian',
    'id': 'Indonesian',
    'is': 'Icelandic',
    'it': 'Italian',
    'ja': 'Japanese',
    'jw': 'Javanese',
    'km': 'Khmer',
    'kn': 'Kannada',
    'ko': 'Korean',
    'la': 'Latin',
    'lv': 'Latvian',
    'ml': 'Malayalam',
    'mr': 'Marathi',
    'ms': 'Malay',
    'my': 'Myanmar',
    'ne': 'Nepali',
    'nl': 'Dutch',
    'no': 'Norwegian',
    'pa': 'Punjabi',
    'pl': 'Polish',
    'pt': 'Portuguese',
    'ro': 'Romanian',
    'ru': 'Russian',
    'si': 'Sinhala',
    'sk': 'Slovak',
    'sq': 'Albanian',
    'sr': 'Serbian',
    'su': 'Sundanese',
    'sv': 'Swedish',
    'sw': 'Swahili',
    'ta': 'Tamil',
    'te': 'Telugu',
    'th': 'Thai',
    'tl': 'Filipino',
    'tr': 'Turkish',
    'uk': 'Ukrainian',
    'ur': 'Urdu',
    'vi': 'Vietnamese',
    'zh-CN': 'Chinese (Simplified)',
    'zh-TW': 'Chinese (Traditional)',
    'auto': 'Auto Detect'
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
