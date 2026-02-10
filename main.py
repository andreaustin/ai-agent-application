import streamlit as st
from google import genai
import os
import json
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Configure Gemini API
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    client = genai.Client(api_key=api_key)
else:
    st.error("Google API Key not found. Please set it in the .env file.")
    client = None

def get_airport_code(location):
    """Uses Gemini to resolve a location string to its primary 3-letter IATA airport code."""
    if not client:
        return None
    
    prompt = f"""
    Return only the 3-letter IATA airport codes for the nearest, primary airports to: {location}.
    Example: 'New York' -> 'JFK', 'London' -> 'LHR'. Output only the 3 letters (code*) if only one airport.
    If more than one airport then output only up to 3 codes* separated by commas, without any additional text or spacing.
    Example: 'New York' -> 'JFK,EWR,LGA'
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        code = response.text.strip().upper()
        # Basic validation: check if it's 3 letters
        return code
    except Exception as e:
        return f"Error retrieving airport code: {str(e)}"

def get_flights(source, destination, travelers, outbound_date, return_date=None):
    """Returns mock SerpApi Google Flights data."""

    base_url = "https://serpapi.com/search.json?engine=google_flights"
    departure_id = f"&departure_id={get_airport_code(source)}"
    arrival_id = f"&arrival_id={get_airport_code(destination)}"
    currency = "&currency=USD"
    outbound = f"&outbound_date={outbound_date}"
    traveling = f"&adults={travelers}"

    url = f"{base_url}{departure_id}{arrival_id}{currency}{outbound}{traveling}"

    if return_date:
        returning = f"&return_date={return_date}"
        url += returning + f"&type=1" # Round-trip
    else:
        url += f"&type=2" # One-way, if no return date

    url += f"&api_key={os.getenv('SERPAPI_KEY')}"

    response = requests.get(url)
    if response.status_code != 200:
        return f"Error fetching flight data: {response.status_code}\n{response.text}"
    if response.status_code == 401:
        return f"{response.status_code} Unauthorized: Some API error. {response.text}"
    results = response.json()
    best_flights = results["best_flights"]
    return best_flights

def get_travel_plan(source, destination, dates, budget, travelers, interests):
    """Generates a travel plan using gemini-2.5-flash."""
    if not client:
        return "Error: Client not configured."

    prompt = f"""
    You are an expert travel planner AI. Create a detailed travel itinerary based on:
    - Source: {source}
    - Destination: {destination}
    - Dates: {dates}
    - Budget: {budget}
    - Travelers: {travelers}
    - Interests: {interests}
    
    Return a beautiful Markdown response with:
    # 🗓️ Travel Plan: {destination}
    ## ✈️ Overview
    Brief summary of the trip.
    
    ## 📍 Day-by-Day Itinerary
    Detailed daily activities.
    
    ## 🍕 Food & Dining
    Top local recommendations.
    
    ## 💰 Estimated Budget Breakdown
    Costs for activities and stay.
    
    ## 🧳 Packing & Tips
    Essential advice.
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
st.set_page_config(page_title="Travel AI Agent", layout="wide")

st.title("🌍 Your AI Travel Planner")
st.markdown("### *Your personal minimalist travel assistant.*")

with st.sidebar:
    st.header("Trip Configuration")
    with st.form("travel_form"):
        source_city = st.text_input("Source City", placeholder="e.g. New York")
        dest_city = st.text_input("Destination City", placeholder="e.g. Paris")
        
        col1, col2 = st.columns(2)
        with col1:
            outbound_date = st.date_input("Outbound")
        with col2:
            return_date = st.date_input("Return")
            
        budget = st.text_input("Budget", placeholder="e.g. $2000")
        travelers = st.number_input("Travelers", min_value=1, step=1)
        interests = st.text_area("Interests", placeholder="e.g. Art, History, Food")
        
        include_flights = st.checkbox("Include Transportation Details", value=True)
        
        submit_button = st.form_submit_button("Generate Travel Plan", use_container_width=True)

if submit_button:
    if not source_city or not dest_city or not interests:
        st.error("Please fill in Source, Destination, and Interests.")
    else:
        with st.spinner("Crafting your perfect itinerary..."):
            dates = f"{outbound_date} to {return_date}"
            plan = get_travel_plan(source_city, dest_city, dates, budget, travelers, interests)
            
            # Show flights first if selected
            if include_flights:
                st.header("✈️ Best Flights")
                flight_data = get_flights(source_city, dest_city, travelers, outbound_date, return_date)
                
                if isinstance(flight_data, list):
                    # Building a nice markdown table for flight options
                    table_header = "| Airport | Airline | Flight | Departure | Arrival | Duration | Price |\n| :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
                    table_rows = []
                    
                    for group in flight_data:
                        price = f"${group.get('price', 'N/A')}"
                        # Taking details from the first leg of the flight group
                        f = group.get("flights", [{}])[0]
                        airline = f.get("airline", "N/A")
                        f_no = f.get("flight_number", "N/A")
                        dep = f.get("departure_airport", {})
                        arr = f.get("arrival_airport", {}).get("time", "N/A")
                        dur = f"{f.get('duration', 'N/A')}m"
                        airport_id = f.get("departure_airport", {}).get("id", "N/A")
                        airport_name = f.get("departure_airport", {}).get("name", "N/A")
                        airport = f"{airport_name} ({airport_id})"

                        table_rows.append(f"| {airport} | {airline} | {f_no} | {dep} | {arr} | {dur} | **{price}** |")
                    
                    st.markdown(table_header + "\n" + "\n".join(table_rows))
                else:
                    st.error(flight_data)
                
                st.divider()
            
            # Show Travel Plan after flights
            st.markdown(plan)
