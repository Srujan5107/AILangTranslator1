import streamlit as st
import requests
import base64
from gtts import gTTS
from deep_translator import GoogleTranslator
from deep_translator.constants import GOOGLE_LANGUAGES_TO_CODES
from streamlit_lottie import st_lottie

# ---------------- Page Config & Theme ----------------
st.set_page_config(page_title="LingoFlow AI", page_icon="🌐", layout="wide")

# Function to load Lottie animations
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_translate = load_lottieurl("https://lottie.host/79075778-9585-4428-9730-68131349580b/GvXIn9P7vH.json")

# ---------------- Custom CSS: Glassmorphism & Animations ----------------
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    /* Glassmorphism Card */
    .glass-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 2rem;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        margin-bottom: 20px;
    }

    /* Styled Text Areas */
    .stTextArea textarea {
        background: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 15px !important;
        font-size: 1.1rem !important;
    }

    /* Translation Box Display */
    .output-box {
        min-height: 250px;
        background: rgba(0, 0, 0, 0.2);
        border-radius: 15px;
        padding: 20px;
        color: #e0e0e0;
        border: 1px dashed rgba(255,255,255,0.3);
        font-size: 1.1rem;
    }

    /* Custom Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 12px !important;
        height: 3em !important;
        background-color: #ffffff22 !important;
        color: white !important;
        border: 1px solid white !important;
        transition: 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #ffffff44 !important;
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# ---------------- Logic & State ----------------
lang_map = {name.capitalize(): code for name, code in GOOGLE_LANGUAGES_TO_CODES.items()}
language_names = sorted(lang_map.keys())

if 'translated_text' not in st.session_state:
    st.session_state.translated_text = ""
if 'src_lang' not in st.session_state:
    st.session_state.src_lang = "Auto Detect"
if 'targ_lang' not in st.session_state:
    st.session_state.targ_lang = "Spanish"

def swap_languages():
    if st.session_state.src_lang != "Auto Detect":
        old_src = st.session_state.src_lang
        st.session_state.src_lang = st.session_state.targ_lang
        st.session_state.targ_lang = old_src

def autoplay_audio(text, lang):
    if text.strip():
        try:
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save("temp.mp3")
            with open("temp.mp3", "rb") as f:
                data = f.read()
                b64 = base64.b64encode(data).decode()
                md = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
                st.markdown(md, unsafe_allow_html=True)
        except:
            st.error("Audio generation failed for this language.")

# ---------------- UI Layout ----------------
st.markdown("<h1 style='text-align: center; color: white; margin-bottom: 0;'>✨ LingoFlow AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #ddd;'>Next-Gen Neural Translation</p>", unsafe_allow_html=True)

# Animation Header
c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    st_lottie(lottie_translate, height=150, key="main_anim")

# Main Interface Card
with st.container():
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    # Language Selection Row
    l_col1, l_mid, l_col2 = st.columns([4, 1, 4])
    with l_col1:
        src_lang = st.selectbox("From", ["Auto Detect"] + language_names, key="src_lang")
    with l_mid:
        st.write("##")
        st.button("🔄", on_click=swap_languages, help="Swap Languages")
    with l_col2:
        targ_lang = st.selectbox("To", language_names, key="targ_lang")

    # Text Input/Output Row
    t_col1, t_col2 = st.columns(2)
    with t_col1:
        input_text = st.text_area("Input Text", height=250, placeholder="Start typing here...", label_visibility="collapsed")
        if st.button("🔊 Listen", key="listen_in"):
            autoplay_audio(input_text, "en")
            
    with t_col2:
        st.markdown(f'<div class="output-box">{st.session_state.translated_text if st.session_state.translated_text else "Translation appears here..."}</div>', unsafe_allow_html=True)
        out_btn_col1, out_btn_col2 = st.columns(2)
        with out_btn_col1:
            if st.button("🔊 Pronounce", key="listen_out"):
                t_code = lang_map.get(st.session_state.targ_lang, 'es')
                autoplay_audio(st.session_state.translated_text, t_code)
        with out_btn_col2:
            if st.button("📋 Copy", key="copy_btn"):
                st.toast("Text copied to clipboard! (Simulated)")

    # Action Row
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 Translate Now", type="primary"):
        if input_text:
            with st.spinner("Analyzing context..."):
                src = "auto" if src_lang == "Auto Detect" else lang_map[src_lang]
                targ = lang_map[targ_lang]
                translation = GoogleTranslator(source=src, target=targ).translate(input_text)
                st.session_state.translated_text = translation
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- Footer ----------------
st.markdown("<p style='text-align: center; color: rgba(255,255,255,0.5);'>Powered by Google Neural Machine Translation</p>", unsafe_allow_html=True)
