import streamlit as st
import pandas as pd
import re
import streamlit.components.v1 as components

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="Perfume Finder",
    page_icon="💎",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- 2. ANALYTICS ---
def inject_ga4():
    GA_ID = "G-S5NLHL3KFM"
    ga_code = f"""
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{GA_ID}');
    </script>
    """
    components.html(ga_code, height=0, width=0)

inject_ga4()

# --- 3. DATA LOGIC ---
def brutal_clean(text):
    if pd.isna(text): return []
    text = str(text)
    text = re.sub(r"[^a-zA-Z, ]", "", text)
    return [x.strip().upper() for x in text.split(",") if x.strip()]

def generate_stars(score):
    try:
        val = float(score)
        full = int(val)
        full = min(full, 5)
        return "★" * full + "☆" * (5 - full)
    except:
        return "☆☆☆☆☆"

def get_initials(name):
    if not name: return "PF"
    clean = re.sub(r"[^a-zA-Z0-9 ]", "", str(name))
    words = clean.split()
    if len(words) >= 2:
        return (words[0][0] + words[1][0]).upper()
    return clean[:2].upper()

# --- 4. CSS STYLING (SAFE MODE) ---
def load_custom_css():
    # Defined as a variable to prevent SyntaxError
    styles = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600&family=Playfair+Display:wght@600;700&display=swap');

        /* --- ELEGANT TITLE FRAME --- */
        .title-frame {
            border: 3px double #D4AF37;
            padding: 30px;
            margin-bottom: 40px;
            text-align: center;
            background: rgba(0, 0, 0, 0.3);
            box-shadow: 0 0 15px rgba(212, 175, 55, 0.1);
        }

        /* --- SIDEBAR --- */
        section[data-testid="stSidebar"] {
            background-color: #050505 !important;
            border-right: 1px solid #222;
        }
        .stSidebar h2, .stSidebar h3 {
            font-family: 'Playfair Display', serif !important;
            font-size: 12px !important;
            color: #D4AF37 !important;
            margin-bottom: 5px !important;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .stSidebar label p {
            font-size: 11px !important;
            color: #AAA !important;
        }
        .stRadio, .stMultiSelect, .stSlider { margin-bottom: -20px !important; }
        div[role="radiogroup"] { gap: 0px !important; }
        
        /* --- DROPDOWN FIX