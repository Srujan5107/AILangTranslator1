import streamlit as st
import requests
import base64
from gtts import gTTS
from deep_translator import GoogleTranslator
from deep_translator.constants import GOOGLE_LANGUAGES_TO_CODES
from streamlit_lottie import st_lottie
from datetime import datetime

# ---------------- Page Config ----------------
st.set_page_config(page_title="LingoFlow AI", page_icon="🌐", layout="wide")

# ---------------- Session State Initialization ----------------
if 'history' not in st.session_state:
    st.session_state.history = []
if 'translated_text' not in st.session_state:
    st.session_state.translated_text = ""
if 'src_lang' not in st.session_state:
    st.session_state.src_lang = "Auto Detect"
if 'targ_lang' not in st.session_state:
    st.session_state.targ_lang = "Spanish"
if 'input_val' not in st.session_state:
    st.session_state.input_val = ""

# ---------------- Helper Functions ----------------
def load_lottieurl(url: str):
    r = requests.get(url)
    return r.json() if r.status_code == 200 else None

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
        except Exception:
            st.error("Audio unavailable for this language.")

# ---------------- Custom CSS ----------------
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #1e1e2f 0%, #2d3436 100%); color: white; }
    
    /* Glassmorphism Card */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }

    /* History Sidebar Item */
    .history-item {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
        border-left: 4px solid #6c5ce7;
    }
    
    .stTextArea textarea {
        background: rgba(0, 0, 0, 0.2) !important;
        color: #fff !important;
        border-radius: 15px !important;
    }

    .output-box {
        min-height: 250px;
        background: rgba(108, 92, 231, 0.1);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(108, 92, 231, 0.3);
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- Sidebar: History ----------------
with st.sidebar:
    st.title("📜 Translation History")
    if st.button("🗑️ Clear History"):
        st.session_state.history = []
        st.rerun()
    
    st.markdown("---")
    
    if not st.session_state.history:
        st.info("No recent translations.")
    else:
        for idx, item in enumerate(reversed(st.session_state.history)):
            with st.container():
                st.markdown(f"""
                <div class="history-item">
                    <small style='color: #a29bfe;'>{item['time']}</small><br>
                    <b>{item['src']} → {item['targ']}</b><br>
                    <div style='font-size: 0.85rem; opacity: 0.8;'>{item['input'][:50]}...</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Restore ##{len(st.session_state.history)-idx}", key=f"rest_{idx}"):
                    st.session_state.input_val = item['input']
                    st.session_state.translated_text = item['output']
                    st.session_state.src_lang = item['src']
                    st.session_state.targ_lang = item['targ']
                    st.rerun()

# ---------------- Main UI ----------------
lang_map = {name.capitalize(): code for name, code in GOOGLE_LANGUAGES_TO_CODES.items()}
language_names = sorted(lang_map.keys())

st.markdown("<h1 style='text-align: center;'>🌐 LingoFlow AI</h1>", unsafe_allow_html=True)

# Layout Container
with st.container():
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    # Controls
    col_a, col_b, col_c = st.columns([4, 1, 4])
    with col_a:
        src_lang = st.selectbox("From", ["Auto Detect"] + language_names, key="src_lang")
    with col_b:
        st.write("##")
        st.button("🔄", on_click=swap_languages)
    with col_c:
        target_lang = st.selectbox("To", language_names, key="targ_lang")

    # Input/Output
    t_col1, t_col2 = st.columns(2)
    with t_col1:
        input_text = st.text_area("Source Text", value=st.session_state.input_val, height=250, placeholder="Type to translate...", label_visibility="collapsed")
        if st.button("🔊 Listen"):
            autoplay_audio(input_text, "en")
            
    with t_col2:
        st.markdown(f'<div class="output-box">{st.session_state.translated_text if st.session_state.translated_text else "<i style=\'color:gray\'>Translation will appear here...</i>"}</div>', unsafe_allow_html=True)
        if st.button("🔊 Pronounce"):
            t_code = lang_map.get(st.session_state.targ_lang, 'es')
            autoplay_audio(st.session_state.translated_text, t_code)

    # Translate Button Logic
    if st.button("🚀 Translate Now", use_container_width=True, type="primary"):
        if input_text.strip():
            src_code = "auto" if src_lang == "Auto Detect" else lang_map[src_lang]
            targ_code = lang_map[target_lang]
            
            result = GoogleTranslator(source=src_code, target=targ_code).translate(input_text)
            
            # Update States
            st.session_state.translated_text = result
            st.session_state.input_val = input_text
            
            # Add to History
            new_entry = {
                "time": datetime.now().strftime("%H:%M:%S"),
                "src": src_lang,
                "targ": target_lang,
                "input": input_text,
                "output": result
            }
            st.session_state.history.append(new_entry)
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
