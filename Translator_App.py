import streamlit as st
import requests
import time
import os
from gtts import gTTS
from deep_translator import GoogleTranslator
from deep_translator.constants import GOOGLE_LANGUAGES_TO_CODES

# ---------------- Page Config ----------------
st.set_page_config(page_title="Language Translator", layout="wide")

# ---------------- Custom CSS for UI ----------------
st.markdown("""
<style>
    /* Ensure input and output boxes have equal height and styling */
    .stTextArea textarea {
        height: 250px !important;
    }
    .output-container {
        border: 1px solid #dcdcdc;
        border-radius: 5px;
        padding: 10px;
        height: 250px;
        background-color: #f9f9f9;
        overflow-y: auto;
        position: relative;
    }
    /* Dark mode adjustments */
    [data-theme="dark"] .output-container {
        background-color: #1e1e1e;
        border-color: #444;
    }
    /* Aligning the audio buttons to the bottom right */
    .audio-row {
        display: flex;
        justify-content: flex-end;
        margin-top: -45px;
        margin-right: 10px;
        position: relative;
        z-index: 10;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- Helper Functions ----------------
def play_voice(text, lang, filename):
    if text.strip():
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(filename)
        return filename
    return None

# ---------------- Translator Setup ----------------
lang_map = {name.capitalize(): code for name, code in GOOGLE_LANGUAGES_TO_CODES.items()}
language_names = sorted(lang_map.keys())

# ---------------- Header ----------------
st.markdown("<h1 style='text-align:center;'>🌐 Language Translator</h1>", unsafe_allow_html=True)

# ---------------- Main Layout ----------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Input Text")
    input_text = st.text_area(" ", height=250, placeholder="Enter text here...", label_visibility="collapsed")
    
    # Bottom right button for Input Audio
    c1, c2 = st.columns([0.8, 0.2])
    with c2:
        if st.button("🔊", key="play_input"):
            audio_file = play_voice(input_text, "en", "input.mp3") # Default to English for input
            if audio_file:
                st.audio(audio_file)

with col2:
    st.subheader("Translated Output")
    # Initialize session state for translation
    if "translated_text" not in st.session_state:
        st.session_state.translated_text = ""

    # Display Output in a box that matches input height
    st.markdown(f"""
        <div class="output-container">
            {st.session_state.translated_text if st.session_state.translated_text else "<i>Translation will appear here...</i>"}
        </div>
    """, unsafe_allow_html=True)

    # Bottom right button for Output Audio
    c1, c2 = st.columns([0.8, 0.2])
    with c2:
        if st.button("🔊", key="play_output"):
            if st.session_state.translated_text:
                # Get the code for the selected target language
                target_lang_code = lang_map.get(st.session_state.get('last_target_lang', 'Spanish'), 'es')
                audio_file = play_voice(st.session_state.translated_text, target_lang_code, "output.mp3")
                if audio_file:
                    st.audio(audio_file)

# ---------------- Controls ----------------
st.markdown("---")
ctrl1, ctrl2, ctrl3 = st.columns([2, 2, 1])

with ctrl1:
    source_language = st.selectbox("From", ["Auto Detect"] + language_names)
with ctrl2:
    target_language = st.selectbox("To", language_names, index=language_names.index("Spanish"))
with ctrl3:
    st.write("##")
    translate_btn = st.button("🚀 Translate", use_container_width=True)

# ---------------- Translation Logic ----------------
if translate_btn:
    if not input_text.strip():
        st.warning("Please enter text.")
    else:
        with st.spinner("Translating..."):
            src_code = "auto" if source_language == "Auto Detect" else lang_map[source_language]
            targ_code = lang_map[target_language]
            
            translated = GoogleTranslator(source=src_code, target=targ_code).translate(input_text)
            st.session_state.translated_text = translated
            st.session_state.last_target_lang = target_language
            st.rerun()
