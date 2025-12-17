import streamlit as st
import requests
import time
from gtts import gTTS
from deep_translator import GoogleTranslator
from deep_translator.constants import GOOGLE_LANGUAGES_TO_CODES
from streamlit_lottie import st_lottie

# ---------------- Page Config ----------------
st.set_page_config(page_title="Language Translator", layout="wide")

# ---------------- CSS Animations ----------------
st.markdown("""
<style>
.fade-in {
    animation: fadeIn 1.5s ease-in-out;
}
@keyframes fadeIn {
    from {opacity: 0;}
    to {opacity: 1;}
}
.slide-up {
    animation: slideUp 1s ease;
}
@keyframes slideUp {
    from {transform: translateY(20px); opacity:0;}
    to {transform: translateY(0); opacity:1;}
}
</style>
""", unsafe_allow_html=True)

# ---------------- Load Lottie ----------------
def load_lottie(url):
    r = requests.get(url)
    return r.json() if r.status_code == 200 else None

loading_anim = load_lottie("https://assets2.lottiefiles.com/packages/lf20_jcikwtux.json")
success_anim = load_lottie("https://assets2.lottiefiles.com/packages/lf20_touohxv0.json")

# ---------------- Header ----------------
st.markdown("<h1 class='fade-in' style='text-align:center;'>🌐 Language Translator</h1>", unsafe_allow_html=True)

# ---------------- Sidebar Controls ----------------
st.sidebar.header("🎛️ Controls")

dark_mode = st.sidebar.toggle("🌙 Dark Mode")

typing_speed = st.sidebar.slider(
    "⌨️ Typing Animation Speed (ms)",
    min_value=10,
    max_value=200,
    value=50
)

speech_speed = st.sidebar.slider(
    "🔊 Speech Speed",
    min_value=0.5,
    max_value=2.0,
    value=1.0,
    step=0.1
)

enable_tts = st.sidebar.checkbox("Enable Text-to-Speech", value=True)

# ---------------- Dark Mode ----------------
if dark_mode:
    st.markdown("""
    <style>
    body {background-color: #0e1117; color: white;}
    textarea {background-color:#1e1e1e !important; color:white !important;}
    </style>
    """, unsafe_allow_html=True)

# ---------------- Translator ----------------
translator = GoogleTranslator(source="auto")

lang_map = {name.capitalize(): code for name, code in GOOGLE_LANGUAGES_TO_CODES.items()}
language_names = sorted(lang_map.keys())

# ---------------- Layout ----------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Input Text")
    input_text = st.text_area("", height=200, placeholder="Type text here...")

with col2:
    st.subheader("Translated Output")
    output_box = st.empty()

# ---------------- Language Selection ----------------
st.markdown("---")
c1, c2, c3 = st.columns([2, 2, 1])

with c1:
    source_language = st.selectbox("From", ["Auto Detect"] + language_names)

with c2:
    target_language = st.selectbox("To", language_names, index=language_names.index("Spanish"))

with c3:
    translate_btn = st.button("🚀 Translate")

# ---------------- Typing Effect ----------------
def typing_effect(text, speed):
    displayed = ""
    for char in text:
        displayed += char
        output_box.markdown(
            f"<div class='slide-up'>{displayed}</div>",
            unsafe_allow_html=True
        )
        time.sleep(speed / 1000)

# ---------------- Translation Logic ----------------
if translate_btn:
    if not input_text.strip():
        st.warning("⚠️ Please enter text to translate.")
    else:
        with st.spinner("Translating..."):
            if loading_anim:
                st_lottie(loading_anim, height=120)

            try:
                translator.source = "auto" if source_language == "Auto Detect" else lang_map[source_language]
                translator.target = lang_map[target_language]

                translated_text = translator.translate(input_text)

                typing_effect(translated_text, typing_speed)

                if success_anim:
                    st_lottie(success_anim, height=100)

                # ---------------- Text to Speech ----------------
                if enable_tts:
                    tts = gTTS(text=translated_text, lang=lang_map[target_language], slow=False)
                    tts.save("speech.mp3")
                    st.audio("speech.mp3")

                st.success("✅ Translation completed!")

            except Exception as e:
                st.error(f"Translation Error: {e}")
