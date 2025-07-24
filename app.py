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

# Custom CSS
st.markdown("""
<style>
    .ingredient-tag {
        background-color: #e3f2fd;
        border-radius: 20px;
        padding: 5px 15px;
        margin: 5px;
        display: inline-block;
        font-size: 14px;
        color: #1976d2;
        border: 1px solid #bbdefb;
    }
    .recipe-card {
        background-color: #f5f5f5;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .recipe-title {
        color: #2e7d32;
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .remove-btn {
        background-color: #ff6b6b;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 2px 8px;
        font-size: 12px;
        cursor: pointer;
        margin-left: 5px;
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

# Header
st.title("🍳 Smart Recipe Generator")
st.markdown("Transform your ingredients into delicious recipes with AI!")

# Get API key from Streamlit secrets
api_key = st.secrets.get("GEMINI_API_KEY", "")

if not api_key:
    st.error("⚠️ Please add your GEMINI_API_KEY to Streamlit secrets!")
    st.info("""
    ### How to add your API key:
    1. Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
    2. Go to your app settings in Streamlit Cloud
    3. Navigate to the 'Secrets' section
    4. Add: `GEMINI_API_KEY = "your-api-key-here"`
    5. Save and restart the app
    """)
    
    # Manual API key input as fallback
    manual_key = st.text_input("Or enter your API key here (temporary):", type="password")
    if manual_key:
        api_key = manual_key
    else:
        st.stop()

# Configure Gemini with error handling
try:
    genai.configure(api_key=api_key)
    st.session_state.api_configured = True
except Exception as e:
    st.error(f"Error configuring API: {str(e)}")
    st.stop()

# Safety settings for content generation
safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE"
    }
]

# Generation configuration
generation_config = {
    "temperature": 0.7,
    "top_p": 0.9,
    "max_output_tokens": 2048,
}

# Sidebar filters
with st.sidebar:
    st.header("🎯 Recipe Preferences")
    
    # Cooking time preference
    time_pref = st.select_slider(
        "⏱️ Cooking Time",
        options=["Under 15 min", "15-30 min", "30-45 min", "45-60 min", "Over 1 hour"],
        value="30-45 min"
    )
    
    # Difficulty level
    difficulty = st.radio(
        "📊 Difficulty Level",
        ["Easy", "Medium", "Hard", "Any"],
        index=0
    )
    
    # Dietary restrictions
    dietary = st.multiselect(
        "🥗 Dietary Restrictions",
        ["Vegetarian", "Vegan", "Gluten-Free", "Dairy-Free", "Nut-Free", "Low-Carb", "Keto"],
        default=[]
    )
    
    # Cuisine type
    cuisine = st.selectbox(
        "🌍 Cuisine Type",
        ["Any", "Italian", "Asian", "Mexican", "Indian", "Mediterranean", "American", "French"]
    )
    
    # Meal type
    meal_type = st.selectbox(
        "🍽️ Meal Type",
        ["Any", "Breakfast", "Lunch", "Dinner", "Snack", "Dessert"]
    )
    
    st.markdown("---")
    
    # Debug info (optional)
    with st.expander("🔧 Debug Info"):
        st.write(f"API Configured: {st.session_state.api_configured}")
        st.write(f"Ingredients Count: {len(st.session_state.ingredients_list)}")

# Main content area
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("🛒 Your Ingredients")
    
    # Input methods
    tab1, tab2 = st.tabs(["➕ Add Single", "📋 Add Multiple"])
    
    with tab1:
        # Single ingredient input
        single_ingredient = st.text_input("Enter an ingredient:")
        if st.button("Add Ingredient", key="add_single"):
            if single_ingredient:
                st.session_state.ingredients_list.append(single_ingredient.strip())
                st.success(f"Added: {single_ingredient}")
                st.rerun()
    
    with tab2:
        # Multiple ingredients input
        ingredients_input = st.text_area(
            "Enter multiple ingredients (one per line or comma-separated):",
            height=100
        )
        if st.button("Add All", key="add_multiple"):
            if ingredients_input:
                # Handle both comma-separated and newline-separated input
                if ',' in ingredients_input:
                    new_items = [i.strip() for i in ingredients_input.split(",") if i.strip()]
                else:
                    new_items = [i.strip() for i in ingredients_input.split("\n") if i.strip()]
                
                st.session_state.ingredients_list.extend(new_items)
                st.success(f"Added {len(new_items)} ingredients!")
                st.rerun()
    
    # Display current ingredients
    if st.session_state.ingredients_list:
        st.markdown("### Current Ingredients:")
        
        # Create columns for ingredient display
        ingredients_container = st.container()
        with ingredients_container:
            for idx, ing in enumerate(st.session_state.ingredients_list):
                col_ing, col_btn = st.columns([4, 1])
                with col_ing:
                    st.markdown(f"<span class='ingredient-tag'>🥘 {ing}</span>", unsafe_allow_html=True)
                with col_btn:
                    if st.button("❌", key=f"remove_{idx}"):
                        st.session_state.ingredients_list.pop(idx)
                        st.rerun()
        
        # Action buttons
        col_clear, col_export = st.columns(2)
        with col_clear:
            if st.button("🗑️ Clear All", type="secondary"):
                st.session_state.ingredients_list = []
                st.rerun()
        with col_export:
            # Export ingredients list
            ingredients_text = "\n".join(st.session_state.ingredients_list)
            st.download_button(
                "📥 Export List",
                ingredients_text,
                "ingredients.txt",
                "text/plain"
            )
    else:
        st.info("👆 Start by adding some ingredients above!")

with col2:
    st.subheader("🔥 Recipe Generation")
    
    if st.session_state.ingredients_list:
        st.write(f"**Ingredients ready:** {len(st.session_state.ingredients_list)}")
        
        # Recipe count selector
        recipe_count = st.slider("Number of recipes to generate:", 1, 5, 3)
        
        if st.button("🎯 Generate Recipes", type="primary", use_container_width=True):
            with st.spinner("🧑‍🍳 Creating your personalized recipes..."):
                # Create the prompt
                dietary_text = f"Dietary restrictions: {', '.join(dietary)}" if dietary else "No dietary restrictions"
                cuisine_text = f"Cuisine preference: {cuisine}" if cuisine != "Any" else ""
                meal_text = f"Meal type: {meal_type}" if meal_type != "Any" else ""
                
                prompt = f"""
                Create exactly {recipe_count} unique and detailed recipes using these ingredients: {', '.join(st.session_state.ingredients_list)}
                
                Requirements:
                - Cooking time: {time_pref}
                - Difficulty level: {difficulty}
                - {dietary_text}
                {cuisine_text}
                {meal_text}
                
                For each recipe, provide:
                1. Recipe Name (creative and appealing)
                2. Brief Description (2-3 sentences)
                3. Prep Time and Cook Time
                4. Servings
                5. Complete Ingredients List with measurements
                6. Step-by-step Instructions (numbered)
                7. Chef's Tips or Variations
                8. Nutritional highlights (brief)
                
                Format the output clearly with headers and bullet points.
                Make the recipes practical and delicious!
                """
                
                try:
                    # Initialize the model
                    model = genai.GenerativeModel(
                        model_name='gemini-pro',
                        safety_settings=safety_settings,
                        generation_config=generation_config
                    )
                    
                    # Generate content
                    response = model.generate_content(prompt)
                    
                    if response.text:
                        st.session_state.recipes = response.text
                        st.success("✅ Recipes generated successfully!")
                    else:
                        st.error("No response received. Please try again.")
                        
                except Exception as e:
                    st.error(f"⚠️ Error generating recipes: {str(e)}")
                    
                    # Provide helpful debugging information
                    with st.expander("🔍 Error Details"):
                        st.code(str(e))
                        st.write("Possible solutions:")
                        st.write("1. Check if your API key is valid")
                        st.write("2. Ensure you have access to the Gemini API")
                        st.write("3. Try refreshing the page")
                        st.write("4. Check your internet connection")
                        
                        # Try to list available models
                        try:
                            st.write("\nAvailable models:")
                            for m in genai.list_models():
                                if 'generateContent' in m.supported_generation_methods:
                                    st.write(f"- {m.name}")
                        except:
                            st.write("Could not fetch model list")
    else:
        st.info("👈 Add ingredients from the left panel to get started!")
        
        # Quick ingredient suggestions
        st.markdown("### 🎲 Quick Add Suggestions:")
        suggestions = ["Chicken", "Rice", "Tomatoes", "Onions", "Garlic", 
                      "Pasta", "Cheese", "Eggs", "Potatoes", "Bell Peppers"]
        
        cols = st.columns(5)
        for idx, suggestion in enumerate(suggestions):
            with cols[idx % 5]:
                if st.button(suggestion, key=f"sugg_{idx}"):
                    st.session_state.ingredients_list.append(suggestion)
                    st.rerun()

# Display generated recipes
if st.session_state.recipes:
    st.markdown("---")
    st.markdown("## 📖 Your Personalized Recipes")
    
    # Display recipes in a nice format
    st.markdown(st.session_state.recipes)
    
    # Action buttons for recipes
    col_save, col_share, col_new = st.columns(3)
    
    with col_save:
        # Save recipes
        st.download_button(
            "💾 Save Recipes",
            st.session_state.recipes,
            f"recipes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "text/plain"
        )
    
    with col_share:
        # Copy to clipboard (using a workaround)
        if st.button("📋 Copy to Clipboard"):
            st.info("Select the text above and copy manually (Ctrl+C / Cmd+C)")
    
    with col_new:
        if st.button("🔄 Generate New"):
            st.session_state.recipes = []
            st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; padding: 20px;'>
        <p>🍳 Smart Recipe Generator | Powered by Google Gemini AI</p>
        <p>Made with ❤️ using Streamlit</p>
    </div>
    """,
    unsafe_allow_html=True
)
