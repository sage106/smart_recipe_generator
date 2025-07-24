import streamlit as st
import google.generativeai as genai
import json
import os
from datetime import datetime
import re

# Configure page
st.set_page_config(
    page_title="Smart Recipe Generator",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Main Title */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    /* Ingredient Tags */
    .ingredient-tag {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border-radius: 25px;
        padding: 8px 20px;
        margin: 5px;
        display: inline-block;
        font-size: 14px;
        font-weight: 500;
        box-shadow: 0 4px 15px rgba(245, 87, 108, 0.3);
        transition: all 0.3s ease;
    }
    
    .ingredient-tag:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(245, 87, 108, 0.4);
    }
    
    /* Recipe Cards */
    .recipe-card {
        background: white;
        border-radius: 20px;
        padding: 30px;
        margin: 20px 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
        transition: all 0.3s ease;
    }
    
    .recipe-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }
    
    /* Recipe Title */
    .recipe-title {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 28px;
        font-weight: 700;
        margin-bottom: 15px;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 10px 25px;
        border-radius: 25px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Primary Button Override */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        box-shadow: 0 4px 15px rgba(245, 87, 108, 0.3);
    }
    
    /* Info Boxes */
    .info-box {
        background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
        border-left: 5px solid #0284c7;
        padding: 20px;
        border-radius: 10px;
        margin: 15px 0;
    }
    
    /* Success Messages */
    .success-box {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        border-left: 5px solid #059669;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    /* Stats Cards */
    .stat-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 5px 20px rgba(0,0,0,0.08);
        border: 1px solid #e0e0e0;
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
    }
    
    .stat-number {
        font-size: 32px;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 15px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        font-weight: 600;
        padding: 10px 20px;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        padding: 10px 15px;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Loading Animation */
    .loading-text {
        background: linear-gradient(90deg, #667eea, #764ba2, #667eea);
        background-size: 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradient 2s ease infinite;
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        100% { background-position: 200% 50%; }
    }
    
    /* Quick Add Buttons */
    .quick-add-btn {
        background: white;
        border: 2px solid #e0e0e0;
        color: #4a5568;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: 500;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .quick-add-btn:hover {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-color: transparent;
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "ingredients_list" not in st.session_state:
    st.session_state.ingredients_list = []
if "recipes" not in st.session_state:
    st.session_state.recipes = []
if "api_configured" not in st.session_state:
    st.session_state.api_configured = False
if "recipe_count" not in st.session_state:
    st.session_state.recipe_count = 0

# Animated Header
st.markdown("""
<div class="main-header">
    <h1 style="margin: 0; font-size: 3rem;">🍳 Smart Recipe Generator</h1>
    <p style="margin: 10px 0 0 0; font-size: 1.2rem; opacity: 0.9;">Transform your ingredients into culinary masterpieces with AI</p>
</div>
""", unsafe_allow_html=True)

# Get API key from Streamlit secrets
api_key = st.secrets.get("GEMINI_API_KEY", "")

if not api_key:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="recipe-card" style="text-align: center;">
            <h2 style="color: #dc2626;">⚠️ API Key Required</h2>
            <p>To use this app, you need a Google Gemini API key.</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("📖 How to get your API key", expanded=True):
            st.markdown("""
            1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey) 🔗
            2. Sign in with your Google account
            3. Click on **"Create API Key"**
            4. Copy your API key
            5. Add it to Streamlit secrets or paste below
            """)
        
        manual_key = st.text_input("🔑 Enter your API key here:", type="password", placeholder="AIza...")
        if manual_key:
            api_key = manual_key
        else:
            st.stop()

# Configure Gemini with error handling
try:
    genai.configure(api_key=api_key)
    st.session_state.api_configured = True
except Exception as e:
    st.error(f"❌ Error configuring API: {str(e)}")
    st.stop()

# Sidebar with gradient
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px; margin-bottom: 20px;">
        <h2 style="margin: 0;">🎯 Recipe Preferences</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Model selection with custom styling
    model_options = {
        "⚡ Gemini 1.5 Flash (Fast)": "gemini-1.5-flash",
        "💎 Gemini 1.5 Pro (Advanced)": "gemini-1.5-pro"
    }
    
    selected_model_name = st.selectbox(
        "🤖 AI Model",
        list(model_options.keys()),
        index=0
    )
    
    selected_model = model_options[selected_model_name]
    
    # Preferences with icons
    st.markdown("### ⏱️ Cooking Time")
    time_pref = st.select_slider(
        "",
        options=["⚡ Under 15 min", "🏃 15-30 min", "🚶 30-45 min", "🪑 45-60 min", "🛋️ Over 1 hour"],
        value="🚶 30-45 min",
        label_visibility="collapsed"
    )
    
    st.markdown("### 📊 Difficulty Level")
    difficulty = st.radio(
        "",
        ["👶 Easy", "👦 Medium", "👨 Hard", "🤷 Any"],
        index=0,
        label_visibility="collapsed"
    )
    
    st.markdown("### 🥗 Dietary Restrictions")
    dietary = st.multiselect(
        "",
        ["🌱 Vegetarian", "🌿 Vegan", "🌾 Gluten-Free", "🥛 Dairy-Free", 
         "🥜 Nut-Free", "🥖 Low-Carb", "🥑 Keto"],
        default=[],
        label_visibility="collapsed"
    )
    
    st.markdown("### 🌍 Cuisine Type")
    cuisine = st.selectbox(
        "",
        ["🌐 Any", "🇮🇹 Italian", "🥢 Asian", "🌮 Mexican", "🇮🇳 Indian", 
         "🇬🇷 Mediterranean", "🇺🇸 American", "🇫🇷 French"],
        label_visibility="collapsed"
    )
    
    st.markdown("### 🍽️ Meal Type")
    meal_type = st.selectbox(
        "",
        ["🍴 Any", "🌅 Breakfast", "☀️ Lunch", "🌙 Dinner", "🍿 Snack", "🍰 Dessert"],
        label_visibility="collapsed"
    )

# Main content area with better layout
# Stats row
if st.session_state.ingredients_list:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{len(st.session_state.ingredients_list)}</div>
            <div style="color: #6b7280; font-weight: 600;">Ingredients</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{st.session_state.recipe_count}</div>
            <div style="color: #6b7280; font-weight: 600;">Recipes Generated</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{"✨"}</div>
            <div style="color: #6b7280; font-weight: 600;">Ready to Cook</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Main content columns
col1, col2 = st.columns([3, 2])

with col1:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); padding: 20px; border-radius: 15px;">
        <h2 style="margin: 0 0 20px 0;">🛒 Your Ingredients</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Input methods with enhanced tabs
    tab1, tab2, tab3 = st.tabs(["➕ Add Single", "📋 Add Multiple", "🎲 Quick Add"])
    
    with tab1:
        # Single ingredient input
        single_ingredient = st.text_input("Enter an ingredient:", placeholder="e.g., Tomatoes")
        if st.button("Add Ingredient", key="add_single", use_container_width=True):
            if single_ingredient:
                st.session_state.ingredients_list.append(single_ingredient.strip())
                st.balloons()
                st.success(f"✅ Added: {single_ingredient}")
                st.rerun()
    
    with tab2:
        # Multiple ingredients input
        ingredients_input = st.
