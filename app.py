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

# Get API key from Streamlit secrets
api_key = st.secrets.get("GEMINI_API_KEY", "")

if not api_key:
    st.error("⚠️ Please add your GEMINI_API_KEY to Streamlit secrets!")
    st.info("""
    How to add:
    1. Go to app settings in Streamlit Cloud
    2. Add secret: GEMINI_API_KEY = 'your-api-key'
    """)
    st.stop()

# Configure Gemini
genai.configure(api_key=api_key)

# Your custom CSS
st.markdown("""
<style>
    .ingredient-tag {
        background-color: #e3f2fd;
        border-radius: 20px;
        padding: 5px 15px;
        margin: 5px;
        display: inline-block;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "ingredients_list" not in st.session_state:
    st.session_state.ingredients_list = []
if "recipes" not in st.session_state:
    st.session_state.recipes = []

# Header
st.title("🍳 Smart Recipe Generator")
st.markdown("Generate amazing recipes from your ingredients!")

# Sidebar filters
with st.sidebar:
    st.header("🎯 Preferences")
    time_pref = st.select_slider(
        "⏱️ Cooking Time",
        ["Under 15 min", "15-30 min", "30-45 min", "45-60 min", "Over 1 hour"]
    )
    difficulty = st.radio("📊 Difficulty", ["Easy", "Medium", "Hard", "Any"])
    dietary = st.multiselect("🥗 Dietary", ["Vegetarian", "Vegan", "Gluten-Free", "None"])

# Main content
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("🛒 Add Ingredients")
    
    # Input ingredients
    ingredients_input = st.text_input("Enter ingredients (comma-separated):")
    if st.button("Add") and ingredients_input:
        new_items = [i.strip() for i in ingredients_input.split(",")]
        st.session_state.ingredients_list.extend(new_items)
        st.success(f"Added {len(new_items)} ingredients!")
    
    # Display ingredients
    if st.session_state.ingredients_list:
        st.subheader("Your Ingredients:")
        for ing in st.session_state.ingredients_list:
            st.markdown(f"<span class='ingredient-tag'>{ing}</span>", unsafe_allow_html=True)
        
        if st.button("Clear All"):
            st.session_state.ingredients_list = []
            st.rerun()

with col2:
    st.subheader("🔥 Generate Recipes")
    
    if st.session_state.ingredients_list:
        if st.button("Generate Recipes", type="primary"):
            with st.spinner("Creating recipes..."):
                prompt = f"""
                Create 3 recipes using these ingredients: {', '.join(st.session_state.ingredients_list)}
                Time: {time_pref}
                Difficulty: {difficulty}
                Dietary: {', '.join(dietary)}
                
                Format each recipe with:
                - Name
                - Description
                - Cooking time
                - Instructions (numbered)
                - Tips
                """
                
                try:
                    model = genai.GenerativeModel('gemini-pro')
                    response = model.generate_content(prompt)
                    st.session_state.recipes = response.text
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    else:
        st.info("Add ingredients to get started!")

# Display recipes
if st.session_state.recipes:
    st.markdown("---")
    st.subheader("📖 Your Recipes")
    st.markdown(st.session_state.recipes)