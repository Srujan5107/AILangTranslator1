import streamlit as st
import requests
import time
import base64
from gtts import gTTS
from deep_translator import GoogleTranslator
from deep_translator.constants import GOOGLE_LANGUAGES_TO_CODES

# ---------------- Page Config ----------------
st.set_page_config(page_title="Language Translator", layout="wide")

# ---------------- Custom CSS for Symmetrical UI ----------------
st.markdown("""
<style>
    /* Fix height of text area and output box to be identical */
    .stTextArea textarea {
        height: 250px !important;
        border-radius: 10px !important;
    }
    .output-box {
        height: 250px;
        border: 1px solid #ccc;
        border-radius: 10px;
        padding: 15px;
        background-color: #fcfcfc;
        overflow-y: auto;
        font-size: 16px;
        color: #31333F;
    }
    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
        .output-box {
            background-color: #0e1117;
            border-color: #444;
            color: white;
        }
    }
    /* Align buttons to the bottom right of their containers */
    .button-container {
        display: flex;
        justify-content: flex-end;
        margin-top: -50px;
        margin-right: 10px;
        position: relative;
        z-index: 99;
    }
    .stButton button {
        border-radius: 20px;
        padding: 0px 10px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- Helper: Auto-Play Audio ----------------
def autoplay_audio(text, lang):
    """Generates audio and injects a hidden autoplaying HTML tag."""
    if text.strip():
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save("temp_audio.mp3")
        with open("temp_audio.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f"""
                <audio autoplay="true">
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
                """
            st.markdown(md, unsafe_allow_html=True)

# ---------------- Translator Setup ----------------
lang_map = {name.capitalize(): code for name, code in GOOGLE_LANGUAGES_TO_CODES.items()}
language_names = sorted(lang_map.keys())

if "translated_text" not in st.session_state:
    st.session_state.translated_text = ""

# ---------------- Main UI ----------------
st.markdown("<h1 style='text-align:center;'>🌐 Language Translator</h1>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Input Text")
    input_text = st.text_area("Input", height=250, placeholder="Type something...", label_visibility="collapsed")
    # Position the speaker button in the bottom right
    st.markdown('<div class="button-container">', unsafe_allow_html=True)
    if st.button("🔊", key="in_voice"):
        autoplay_audio(input_text, "en") # Assumes English input for voice
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.subheader("Translated Output")
    # Display results in a styled div
    st.markdown(f"""
        <div class="output-box">
            {st.session_state.translated_text if st.session_state.translated_text else "<span style='color:gray'>Translation will appear here...</span>"}
        </div>
    """, unsafe_allow_html=True)
    
    # Position the speaker button in the bottom right
    st.markdown('<div class="button-container">', unsafe_allow_html=True)
    if st.button("🔊", key="out_voice"):
        if st.session_state.translated_text:
            t_lang = lang_map.get(st.session_state.get('last_lang', 'Spanish'), 'es')
            autoplay_audio(st.session_state.translated_text, t_lang)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- Control Row ----------------
st.markdown("<br>", unsafe_allow_html=True)
c1, c2, c3 = st.columns([2, 2, 1])

with c1:
    source_lang = st.selectbox("From", ["Auto Detect"] + language_names)
with c2:
    target_lang = st.selectbox("To", language_names, index=language_names.index("Spanish"))
with c3:
    st.write("##") # Align with select boxes
    if st.button("🚀 Translate", use_container_width=True):
        if input_text:
            src = "auto" if source_lang == "Auto Detect" else lang_map[source_lang]
            targ = lang_map[target_lang]
            res = GoogleTranslator(source=src, target=targ).translate(input_text)
            st.session_state.translated_text = res
            st.session_state.last_lang = target_lang
            st.rerun()
