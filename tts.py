import streamlit as st
from gtts import gTTS
import io
import tempfile
import os

def text_to_speech(text, lang):
    """
    Convert text to speech using gTTS
    
    Args:
        text (str): The text to convert to speech
        lang (str): ISO language code (e.g., 'en', 'es', 'fr')
        
    Returns:
        BytesIO: In-memory audio file
    """
    # Map language codes for compatibility with gTTS
    lang_mapping = {
        'zh-CN': 'zh-cn',
        'zh-TW': 'zh-tw',
        # Add other mappings as needed
    }
    
    # Use the mapped language code or the original one
    tts_lang = lang_mapping.get(lang, lang)
    
    try:
        # Create a temporary file to store the audio
        audio_bytes = io.BytesIO()
        
        # Generate the speech
        tts = gTTS(text=text, lang=tts_lang, slow=False)
        tts.write_to_fp(audio_bytes)
        
        # Reset the pointer to the beginning of the BytesIO object
        audio_bytes.seek(0)
        
        return audio_bytes
        
    except Exception as e:
        raise Exception(f"TTS error: {str(e)}")
