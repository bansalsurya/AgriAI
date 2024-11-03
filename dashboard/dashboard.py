import streamlit as st
import requests
from geopy.geocoders import Nominatim
from datetime import datetime
from typing import Dict, Tuple, List
import math
from llama_cpp import Llama
import os
from time import time


@st.cache_data(ttl=3600)
def fetch_weather_data(url: str, params: Dict) -> Dict:
    return requests.get(url, params=params).json()

@st.cache_data(ttl=86400)
def fetch_soil_data(url: str, params: Dict) -> Dict:
    headers = {'Accept': 'application/json'}
    return requests.get(url, params=params, headers=headers).json()

@st.cache_data(ttl=300)
def get_location_from_ip() -> Tuple[float, float, str]:
    try:
        response = requests.get("http://ip-api.com/json", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return (
                data.get('lat'),
                data.get('lon'),
                f"{data.get('city', '')}, {data.get('regionName', '')}, {data.get('country', '')}"
            )
        return None, None, None
    except Exception as e:
        st.error(f"Error getting location: {e}")
        return None, None, None

@st.cache_data(ttl=3600)
def geocode_location(location_input: str) -> Tuple[float, float, str]:
    try:
        geolocator = Nominatim(user_agent="crop_advisor")
        if location_input.isdigit() and len(location_input) == 6:
            location = geolocator.geocode(f"{location_input}, India", timeout=5)
        else:
            location = geolocator.geocode(location_input, timeout=5)
        
        if location:
            return location.latitude, location.longitude, location.address
        return None, None, None
    except Exception as e:
        st.error(f"Error geocoding location: {e}")
        return None, None, None

def main():
        st.title("Advanced Soil and Weather Analysis System")
        
        col1, col2 = st.columns(2)
        with col1:
            choice = st.radio("Choose location input:", ("Enter Location", "Current Location"))
        
        analyzer = SoilWeatherAnalyzer()
        advisor = CropAdvisorLLM()
        # Initialize variables
        lat = None
        lon = None
        address = None
        
        # Handle location input
        if choice == "Current Location":
            if st.button("Get Current Location"):
                with st.spinner("Fetching location..."):
                    lat, lon, address = analyzer.get_current_location()
                    if not all([lat, lon, address]):
                        st.error("Could not fetch current location. Please try entering location manually.")
        else:
            location_input = st.text_input("Enter location (name or pincode):")
            if location_input:
                with st.spinner("Fetching location..."):
                    lat, lon, address = analyzer.get_location_from_input(location_input)
                    if not all([lat, lon, address]):
                        st.error("Could not find the specified location. Please check and try again.")

        # Only proceed with analysis if we have valid location data
        if all([lat, lon, address]):
            st.success(f"Location found: {address}")
            result = analyzer.analyze_location(lat, lon, address)
            
            if result:
                tabs = st.tabs(["Location & Weather", "Soil Analysis", "Environmental Risks", "Forecast","Crop Advisor"])
                
                with tabs[0]:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("Location Details")
                        st.json(result['coordinates'])
                    with col2:
                        st.subheader("Current Weather")
                        st.json(result['weather_analysis']['current'])

                with tabs[1]:
                    st.subheader("Soil Composition")
                    st.json(result['soil_analysis']['detailed_characteristics']['soil_composition'])
                    st.subheader("Physical Properties")
                    st.json(result['soil_analysis']['detailed_characteristics']['physical_properties'])
                    st.subheader("Chemical Properties")
                    st.json(result['soil_analysis']['detailed_characteristics']['chemical_properties'])
                    st.subheader("Water Characteristics")
                    st.json(result['soil_analysis']['detailed_characteristics']['water_characteristics'])
                    st.subheader("Fertility Indicators")
                    st.json(result['soil_analysis']['detailed_characteristics']['fertility_indicators'])

                with tabs[2]:
                    st.subheader("Environmental Risks")
                    st.json(result['environmental_conditions'])

                with tabs[3]:
                    st.subheader("Weather Forecast")
                    st.json(result['weather_analysis']['forecast'])

                with tabs[4]:
                    st.subheader("Crop Recommendations")
                    with st.spinner("Generating crop recommendations..."):
                        progress_bar = st.progress(0)
                        print(f"\nAnalyzing conditions for {result['region']}")
                        recommendations = advisor.get_recommendations(result)
                        success = print_recommendations(recommendations, result['region'])
                        progress_bar.progress(100)
                        st.write(recommendations)
                        
                        if not success:
                                # Retry with different parameters
                            print("\nRetrying with adjusted parameters...")
                            advisor.llm.context_params.temperature = 0.5
                            recommendations = advisor.get_recommendations(result)
                            print_recommendations(recommendations, result['region'])
                            st.write(recommendations)

                st.session_state['analysis_result'] = result
            else:
                    st.error("Unable to analyze location. Please try again.")

if __name__ == "__main__":
    main()