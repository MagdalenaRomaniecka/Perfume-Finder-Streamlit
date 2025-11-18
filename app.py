import streamlit as st
import pandas as pd

# --- Page Configuration ---
st.set_page_config(
    page_title="Perfume Finder",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CSS: Mobile-First, High Contrast, No Sidebar ---
def load_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600&family=Playfair+Display:wght@600;700&display=swap');

        /* --- GLOBAL DARK THEME --- */
        html, body, [class*="st-"], [class*="css-"] {
            font-family: 'Montserrat', sans-serif;
            color: #E0E0E0;
            background-color: #050505; /* Deepest Black */
        }
        [data-testid="stAppViewContainer"] { background-color: #050505; }
        
        /* REMOVE HEADER & SIDEBAR COMPLETELY */
        [data-testid="stHeader"] { display: none; }
        [data-testid="stSidebarCollapsedControl"] { display: none !important; }
        section[data-testid="stSidebar"] { display: none; }
        
        /* Adjust top padding since header is gone */
        .block-container { padding-top: 2rem !important; }

        /* --- HIGH CONTRAST INPUTS (FIXING READABILITY) --- */
        
        /* 1. Widget Labels (Titles like "Gender") */
        label p {
            color: #D4AF37 !important; /* Gold */
            font-size: 14px !important;
            font-weight: 600 !important;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        /* 2. Radio Buttons (Gender) - CRITICAL FIX FOR DOT VISIBILITY */
        div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p {
            color: #FFFFFF !important; /* Bright White Text */
            font-weight: 500 !important;
        }
        /* Force the outer ring to be Gold */
        div[role="radiogroup"] div[data-baseweb="radio"] div {
            border-color: #D4AF37 !important;
        }
        /* Force the inner filled dot to be Gold when checked */
        div[role="radiogroup"] [aria-checked="true"] div[data-baseweb="radio"] div {
            background-color: #D4AF37 !important;
        }
        
        /* 3. Slider (Rating) */
        div[data-testid="stSlider"] div[data-testid="stMarkdownContainer"] p {
            color: #FFFFFF !important; /* Bright White Numbers */
            font-weight: 600 !important;
        }
        /* Slider Track */
        div[data-testid="stSlider"] div[data-baseweb="slider"] div {
            background-color: #D4AF37 !important;
        }

        /* 4. Multiselect (Notes) */
        .stMultiSelect div[data-baseweb="select"] span {
            color: #FFFFFF !important;
        }
        /* Dropdown options background */
        div[role="listbox"] ul {
            background-color: #1A1A1A !important;
        }
        div[role="listbox"] li {
            color: white !important;
            background-color: #1A1A1A !important;
        }

        /* --- EXPANDER STYLING (Clean Dark Box) --- */
        .streamlit-expanderHeader {
            background-color: #111111 !important;
            border: 1px solid #333 !important;
            color: #D4AF37 !important;
            font-family: 'Montserrat', sans-serif;
            border-radius: 5px;
        }
        
        /* --- PERFUME CARD STYLING (Text Only, Clean) --- */
        .perfume-card {
            background-color: #121212;
            border-top: 1px solid #333;
            border-bottom: 1px solid #333;
            padding: 20px 0; /* Vertical padding only */
            margin-bottom: 0;
        }
        
        .p-name {
            font-family: 'Playfair Display', serif;
            font-size: 18px; /* Standard readable size */
            color: #FFFFFF;
            font-weight: 600;
            margin-bottom: 5px;
            line-height: 1.2;
        }

        .p-rating {
            font-size: 12px;
            color: #D4AF37; 
            font-weight: 700;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }

        .p-notes {
            font-size: 11px;
            color: #888888;
            margin-top: 6px;
            line-height: 1.4;
        }

        .p-link {
            font-size: 10px;
            color: #555;
            text-decoration: none;
            margin-left: 10px;
            border: 1px solid #333;
            padding: 2px 6px;
            border-radius: 4px;
        }

        /* --- HEADER TYPOGRAPHY (Smaller) --- */
        .main-title {
            font-family: 'Playfair Display', serif;
            font-size: 28px; /* Reduced from 42px */
            color: #D4AF37;
            text-align: center;
            margin-bottom: 5px;
            font-weight: 700;
        }
        .sub-title {
            font-family: 'Montserrat', sans-serif;
            font-size: 10px;
            color: #666;
            text-align: center;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 25px;
        }
        </style>
    """, unsafe_allow_html=True)

# --- Data Loading ---
@st.cache_data
def load_data(filepath, cache_buster_v21): # v21 Cache Buster
    try:
        df = pd.read_csv(filepath)
        # Rename
        df.rename(columns={'Name': 'name', 'Gender': 'gender', 'Rating Value': 'score', 'Rating Count': 'ratings', 'Main Accords': 'main_accords', 'url': 'img_link'}, inplace=True)
        
        # Fix glued names
        if 'name' in df.columns and 'gender' in df.columns:
            df['name'] = df.apply(
                lambda row: str(row['name']).replace(str(row['gender']), '').strip() 
                if pd.notna(row['name']) and pd.notna(row['gender']) else row['name'], axis=1
            )
            
        # Map genders
        gender_map = {'for women': 'Female', 'for men': 'Male', 'for women and men': 'Unisex'}
        df['gender'] = df['gender'].map(gender_map)
        
        # Cleanup
        df.dropna(subset=['main_accords', 'name', 'img_link', 'gender'], inplace=True)
        
        # Convert score
        if df['score'].dtype == 'object':
            df['score'] = df['score'].str.replace(',', '.').astype