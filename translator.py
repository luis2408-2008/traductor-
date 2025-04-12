from deep_translator import GoogleTranslator
from langdetect import detect
import time
import streamlit as st

@st.cache_data(ttl=3600)
def get_languages():
    """Get available languages from Google Translator"""
    try:
        return GoogleTranslator().get_supported_languages(as_dict=True)
    except Exception as e:
        st.error(f"Error getting languages: {str(e)}")
        # Return a default dictionary with some common languages
        return {
            'en': 'english', 'es': 'spanish', 'fr': 'french', 
            'de': 'german', 'it': 'italian', 'pt': 'portuguese', 
            'ru': 'russian', 'ja': 'japanese', 'zh-CN': 'chinese (simplified)',
            'ar': 'arabic', 'hi': 'hindi', 'ko': 'korean'
        }

def detect_language(text):
    """Detect the language of the input text"""
    try:
        return detect(text)
    except:
        # Default to English if detection fails
        return 'en'

def translate_text(text, source_lang, target_lang):
    """Translate text from source language to target language"""
    if not text:
        return ""
    
    if source_lang == target_lang:
        return text
    
    # Add a slight delay to avoid hitting rate limits
    time.sleep(0.1)
    
    try:
        # Create translator, handling 'auto' source language
        if source_lang == 'auto':
            translator = GoogleTranslator(source='auto', target=target_lang)
        else:
            translator = GoogleTranslator(source=source_lang, target=target_lang)
        
        # Get translation
        translated = translator.translate(text)
        return translated
    except Exception as e:
        st.error(f"Translation error: {str(e)}")
        return "Error: Could not translate text."
