import streamlit as st
from google import genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    client = genai.Client(api_key=api_key)
else:
    st.error("Google API Key not found. Please set it in the .env file.")
    client = None

def get_travel_plan(source, destination, dates, budget, travelers, interests):
    """Generates a travel plan using gemini-2.5-flash and the new google-genai SDK."""
    if not client:
        return "Error: Client not configured."

    prompt = f"""
    You are an expert travel planner AI. Create a detailed travel itinerary based on the following details:
    - Source: {source}
    - Destination: {destination}
    - Dates: {dates}
    - Budget: {budget}
    - Number of Travelers: {travelers}
    - Interests: {interests}
    
    Please provide:
    1. A day-wise itinerary.
    2. Estimated costs for major activities.
    3. Recommended local food and restaurants.
    4. Travel tips specific to the destination.
    5. Packing essentials.
    
    Format the response with clear headings and bullet points for readability.
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error generating plan: {str(e)}"

# UI Layout
st.set_page_config(page_title="Travel AI Agent", layout="centered")

st.title("🌍 Travel Planning AI Agent")
st.markdown("Your minimalist personal travel assistant.")

with st.form("travel_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        source = st.text_input("Source City", placeholder="e.g. New York")
        start_date = st.date_input("Start Date")
        budget = st.text_input("Budget", placeholder="e.g. $2000")
        
    with col2:
        destination = st.text_input("Destination City", placeholder="e.g. Paris")
        end_date = st.date_input("End Date")
        travelers = st.number_input("Number of Travelers", min_value=1, step=1)
        
    interests = st.text_area("Interests", placeholder="e.g. Art, History, Food, Hiking")
    
    submit_button = st.form_submit_button("Generate Travel Plan")

if submit_button:
    if not source or not destination or not interests:
        st.warning("The following fields must be filled in: Source City, Destination City, Interests")
    else:
        with st.spinner("Planning your dream trip..."):
            dates = f"{start_date} to {end_date}"
            plan = get_travel_plan(source, destination, dates, budget, travelers, interests)
            st.divider()
            st.markdown(plan)
