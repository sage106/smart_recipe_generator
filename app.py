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
        background: #000000;
        color: white;
        border-radius: 20px;
        padding: 30px;
        margin: 20px 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        border: 1px solid #333333;
        transition: all 0.3s ease;
    }
    
    .recipe-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.4);
        border: 1px solid #555555;
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
    
    /* Recipe Generation Section */
    .recipe-generation-section {
        background: #000000;
        color: white;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #333333;
    }
    
    .recipe-generation-section h2 {
        color: white;
        margin: 0 0 20px 0;
    }
    
    .recipe-generation-section p, .recipe-generation-section label {
        color: #e0e0e0 !important;
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
    <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); 
                padding: 25px; 
                border-radius: 20px; 
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.1);">
        <h2 style="margin: 0 0 20px 0; 
                   color: #ffffff; 
                   font-weight: 700; 
                   text-align: center;
                   text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);">
            <span style="font-size: 35px;">🛒</span> Your Ingredients
        </h2>
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
        ingredients_input = st.text_area(
            "Enter multiple ingredients (one per line or comma-separated):",
            height=150,
            placeholder="e.g.,\nChicken\nRice\nBell Peppers\nor\nChicken, Rice, Bell Peppers"
        )
        if st.button("Add All Ingredients", key="add_multiple", use_container_width=True):
            if ingredients_input:
                # Handle both comma-separated and newline-separated input
                if ',' in ingredients_input:
                    new_items = [i.strip() for i in ingredients_input.split(",") if i.strip()]
                else:
                    new_items = [i.strip() for i in ingredients_input.split("\n") if i.strip()]
                
                st.session_state.ingredients_list.extend(new_items)
                st.success(f"✅ Added {len(new_items)} ingredients!")
                st.rerun()
    
    with tab3:
        # Quick ingredient suggestions
        st.markdown("**Popular Ingredients:**")
        
        # Categories of suggestions
        categories = {
            "🥩 Proteins": ["Chicken", "Beef", "Fish", "Tofu", "Eggs", "Shrimp"],
            "🥬 Vegetables": ["Tomatoes", "Onions", "Garlic", "Bell Peppers", "Broccoli", "Spinach"],
            "🍚 Grains": ["Rice", "Pasta", "Quinoa", "Bread", "Couscous", "Noodles"],
            "🧀 Dairy": ["Cheese", "Milk", "Butter", "Yogurt", "Cream", "Sour Cream"]
        }
        
        for category, items in categories.items():
            st.markdown(f"**{category}**")
            cols = st.columns(3)
            for idx, item in enumerate(items):
                with cols[idx % 3]:
                    if st.button(item, key=f"quick_{item}", use_container_width=True):
                        st.session_state.ingredients_list.append(item)
                        st.rerun()
    
    # Display current ingredients
    if st.session_state.ingredients_list:
        st.markdown("### 📝 Current Ingredients:")
        
        # Create a nice display for ingredients
        ingredients_container = st.container()
        with ingredients_container:
            for idx, ing in enumerate(st.session_state.ingredients_list):
                col_ing, col_btn = st.columns([5, 1])
                with col_ing:
                    st.markdown(f"<span class='ingredient-tag'>🥘 {ing}</span>", unsafe_allow_html=True)
                with col_btn:
                    if st.button("❌", key=f"remove_{idx}"):
                        st.session_state.ingredients_list.pop(idx)
                        st.rerun()
        
        # Action buttons
        col_clear, col_export = st.columns(2)
        with col_clear:
            if st.button("🗑️ Clear All", type="secondary", use_container_width=True):
                st.session_state.ingredients_list = []
                st.rerun()
        with col_export:
            # Export ingredients list
            ingredients_text = "\n".join(st.session_state.ingredients_list)
            st.download_button(
                "📥 Export List",
                ingredients_text,
                "ingredients.txt",
                "text/plain",
                use_container_width=True
            )
    else:
        st.info("👆 Start by adding some ingredients above!")

with col2:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #fff5f5 0%, #fee0e0 100%); padding: 20px; border-radius: 15px;">
        <h2 style="margin: 0 0 20px 0;">🔥 Recipe Generation</h2>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.ingredients_list:
        st.write(f"**Ready to cook with {len(st.session_state.ingredients_list)} ingredients!**")
        
        # Recipe count selector
        recipe_count = st.slider("Number of recipes to generate:", 1, 5, 3)
        
        if st.button("🎯 Generate Recipes", type="primary", use_container_width=True):
            with st.spinner("🧑‍🍳 Creating your personalized recipes..."):
                # Clean preferences for prompt
                clean_time = time_pref.split()[-1]
                clean_difficulty = difficulty.split()[-1]
                clean_dietary = [d.split()[-1] for d in dietary]
                clean_cuisine = cuisine.split()[-1]
                clean_meal = meal_type.split()[-1]
                
                # Create the prompt
                dietary_text = f"Dietary restrictions: {', '.join(clean_dietary)}" if clean_dietary else "No dietary restrictions"
                cuisine_text = f"Cuisine preference: {clean_cuisine}" if clean_cuisine != "Any" else ""
                meal_text = f"Meal type: {clean_meal}" if clean_meal != "Any" else ""
                
                prompt = f"""
                Create exactly {recipe_count} unique and detailed recipes using these ingredients: {', '.join(st.session_state.ingredients_list)}
                
                Requirements:
                - Cooking time: {clean_time}
                - Difficulty level: {clean_difficulty}
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
                Make the recipes practical, delicious, and easy to follow!
                """
                
                try:
                    # Initialize the model
                    model = genai.GenerativeModel(selected_model)
                    
                    # Generate content with safety settings
                    generation_config = {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_output_tokens": 2048,
                    }
                    
                    response = model.generate_content(
                        prompt,
                        generation_config=generation_config
                    )
                    
                    if response.text:
                        st.session_state.recipes = response.text
                        st.session_state.recipe_count += recipe_count
                        st.success("✅ Recipes generated successfully!")
                        st.balloons()
                    else:
                        st.error("No response received. Please try again.")
                        
                except Exception as e:
                    st.error(f"⚠️ Error generating recipes: {str(e)}")
                    
                    # Provide helpful debugging information
                    with st.expander("🔍 Error Details"):
                        st.code(str(e))
                        
                        # If the first model fails, try the other one
                        if selected_model == "gemini-1.5-pro":
                            fallback_model = "gemini-1.5-flash"
                        else:
                            fallback_model = "gemini-1.5-pro"
                        
                        st.write(f"Trying fallback model: {fallback_model}...")
                        
                        try:
                            model = genai.GenerativeModel(fallback_model)
                            response = model.generate_content(
                                prompt,
                                generation_config=generation_config
                            )
                            if response.text:
                                st.session_state.recipes = response.text
                                st.session_state.recipe_count += recipe_count
                                st.success(f"✅ Success with {fallback_model}!")
                        except Exception as e2:
                            st.error(f"❌ Fallback also failed: {str(e2)}")
                            st.write("\nPossible solutions:")
                            st.write("1. Check if your API key is valid")
                            st.write("2. Try again in a few moments")
                            st.write("3. Check your API quota at Google AI Studio")
    else:
        st.info("👈 Add ingredients from the left panel to get started!")
        
        # Motivation message
        st.markdown("""
        ### 💡 Recipe Ideas Await!
        
        Add your available ingredients and let AI create amazing recipes tailored to your preferences.
        
        **Pro Tips:**
        - Add at least 3-5 ingredients for best results
        - Mix proteins, vegetables, and grains
        - Don't forget seasonings and spices!
        """)

# Display generated recipes
if st.session_state.recipes:
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; margin: 20px 0;">
        <h2 style="color: #4a5568;">📖 Your Personalized Recipes</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Display recipes in a nice format
    recipes_container = st.container()
    with recipes_container:
        st.markdown("""
        <div class="recipe-card">
        """, unsafe_allow_html=True)
        
        st.markdown(st.session_state.recipes)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Action buttons for recipes
    st.markdown("<br>", unsafe_allow_html=True)
    col_save, col_print, col_share, col_new = st.columns(4)
    
    with col_save:
        # Save recipes
        st.download_button(
            "💾 Save Recipes",
            st.session_state.recipes,
            f"recipes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "text/plain",
            use_container_width=True
        )
    
    with col_print:
        if st.button("🖨️ Print View", use_container_width=True):
            st.info("Use Ctrl+P (or Cmd+P on Mac) to print this page")
    
    with col_share:
        # Copy to clipboard (using a workaround)
        if st.button("📋 Copy Text", use_container_width=True):
            st.info("Select the text above and copy manually (Ctrl+C / Cmd+C)")
    
    with col_new:
        if st.button("🔄 New Recipes", use_container_width=True):
            st.session_state.recipes = []
            st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; padding: 20px; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 15px; margin-top: 40px;'>
        <p style="font-size: 18px; margin-bottom: 10px;">🍳 Smart Recipe Generator</p>
        <p style="font-size: 14px; margin: 5px;">Powered by Google Gemini AI 🤖</p>
        <p style="font-size: 14px; margin: 5px;">Made with ❤️ using Streamlit</p>
        <p style="font-size: 12px; margin-top: 15px; opacity: 0.8;">Transform your ingredients into culinary masterpieces!</p>
    </div>
    """,
    unsafe_allow_html=True
)
