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

# --- 4. CSS STYLING ---
def load_custom_css():
    # Używamy zwykłego st.markdown, żeby uniknąć problemów ze zmiennymi
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600&family=Playfair+Display:wght@600;700&display=swap');

        /* BACKGROUND */
        .stApp {
            background-color: #0E0E0E !important;
            background-image: radial-gradient(circle at 50% 0%, #1a1a1a 0%, #000000 100%) !important;
            background-attachment: fixed !important;
        }
        
        /* FONTS & COLORS */
        * { font-family: 'Montserrat', sans-serif; color: #E0E0E0; }
        h1, h2, h3 { font-family: 'Playfair Display', serif; color: #D4AF37 !important; }
        
        /* REMOVE WHITE HEADER */
        header, [data-testid="stHeader"] {
            background-color: #0E0E0E !important;
            border-bottom: 1px solid #333;
        }

        /* TITLE FRAME */
        .title-frame {
            border: 3px double #D4AF37;
            padding: 30px;
            margin-bottom: 40px;
            text-align: center;
            background: rgba(0, 0, 0, 0.3);
            box-shadow: 0 0 15px rgba(212, 175, 55, 0.1);
        }

        /* DROPDOWN MENU FIX */
        div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"] {
            background-color: #0E0E0E !important;
            border: 1px solid #333 !important;
        }
        li[role="option"] {
             background-color: #0E0E0E !important;
             color: #E0E0E0 !important;
        }
        li[role="option"]:hover, li[role="option"][aria-selected="true"] {
            background-color: #D4AF37 !important;
            color: #000000 !important;
        }
        span[data-baseweb="tag"] {
            background-color: #222 !important;
            color: #D4AF37 !important;
            border: 1px solid #444 !important;
        }

        /* SIDEBAR */
        section[data-testid="stSidebar"] {
            background-color: #050505 !important;
            border-right: 1px solid #222;
        }
        .stRadio, .stMultiSelect, .stSlider { margin-bottom: -20px !important; }
        .stSidebar label p { font-size: 11px !important; color: #AAA !important; }
        
        /* CUSTOM BUTTON */
        a.fragrantica-btn {
            display: inline-block;
            margin-top: 12px;
            padding: 6px 12px;
            border: 1px solid #D4AF37;
            border-radius: 4px;
            color: #D4AF37 !important;
            text-decoration: none;
            font-size: 10px;
            font-weight: bold;
            letter-spacing: 1px;
        }
        a.fragrantica