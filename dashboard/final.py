import streamlit as st
import requests
from geopy.geocoders import Nominatim
from datetime import datetime
from typing import Dict, Tuple, List,Union
import math
from llama_cpp import Llama
import os
from time import time
import pandas as pd
import re

import plotly.express as px
import plotly.graph_objects as go


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
    
class SoilWeatherAnalyzer:
    def __init__(self):
        # Previous initialization code remains the same...
        self.weather_api_key = "3045dd712ffe6e702e3245525ac7fa38"
        self.soil_api_url = "https://api.ambeedata.com/soil/latest/by-lat-lng"
        self.soil_api_key = "x-api-key: 1f0e44ccc22200c91651960f662455ff67777c654f0671ffae861353ebbf689f"

    def get_current_location(self) -> Tuple[float, float, str]:
        return get_location_from_ip()

    def get_location_from_input(self, location_input: str) -> Tuple[float, float, str]:
        return geocode_location(location_input)
    
    def get_season(self, date: datetime) -> str:
        """
        Determine the season based on the given date.
        
        Args:
            date: The date for which to determine the season.
            
        Returns:
            The season as a string (e.g., "Spring", "Summer", "Fall", "Winter").
        """
        month = date.month
        if month in [3, 4, 5]:
            return "Spring"
        elif month in [6, 7, 8]:
            return "Summer"
        elif month in [9, 10, 11]:
            return "Fall"
        else:
            return "Winter"

    def get_weather_data(self, lat: float, lon: float) -> Dict:
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.weather_api_key,
                'units': 'metric'
            }
            
            current_data = fetch_weather_data(
                "https://api.openweathermap.org/data/2.5/weather",
                params
            )
            
            # Modified to get 5 days of forecast (40 data points = 8 points per day * 5 days)
            forecast_params = params.copy()
            forecast_params['cnt'] = 40
            forecast_data = fetch_weather_data(
                "https://api.openweathermap.org/data/2.5/forecast",
                forecast_params
            )
            
            # Filter to ensure we have exactly 5 days of data
            if 'list' in forecast_data:
                unique_dates = set()
                filtered_forecast = []
                
                for item in forecast_data['list']:
                    date = datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d')
                    if date not in unique_dates and len(unique_dates) < 5:
                        unique_dates.add(date)
                        filtered_forecast.append(item)
                
                forecast_data['list'] = filtered_forecast
            
            return {'current': current_data, 'forecast': forecast_data}
        except Exception as e:
            st.error(f"Error fetching weather data: {e}")
            return None

    def determine_detailed_soil_characteristics(self, lat: float, lon: float, climate: str, rainfall: float) -> Dict:
        """Determine detailed soil characteristics based on location and climate data"""
        # Latitude-based climate zone estimation
        if abs(lat) < 23.5:
            climate_zone = "tropical"
        elif abs(lat) < 35:
            climate_zone = "subtropical"
        else:
            climate_zone = "temperate"

        # Base characteristics
        characteristics = {
            "soil_types": [],
            "texture": "",
            "organic_matter": "",
            "water_retention": "",
            "pH_range": "",
            "fertility": "",
            "additional_features": []
        }

        # Determine characteristics based on climate and rainfall
        if climate.lower() in ['desert', 'clear'] and rainfall < 250:
            characteristics.update({
                "soil_types": ["Desert sandy soil", "Arid soil"],
                "texture": "Coarse and sandy",
                "organic_matter": "Very low",
                "water_retention": "Poor",
                "pH_range": "8.0-8.8 (Alkaline)",
                "fertility": "Low",
                "additional_features": [
                    "High salt content",
                    "Excellent drainage",
                    "Low nutrient content",
                    "Susceptible to wind erosion"
                ]
            })
        elif climate.lower() in ['rain', 'thunderstorm'] and rainfall > 2000:
            characteristics.update({
                "soil_types": ["Lateritic soil", "Red soil"],
                "texture": "Clay-like when wet",
                "organic_matter": "Medium to high",
                "water_retention": "High",
                "pH_range": "4.5-5.5 (Acidic)",
                "fertility": "Medium",
                "additional_features": [
                    "Rich in iron and aluminum oxides",
                    "Heavily leached",
                    "Good drainage",
                    "High in mineral content"
                ]
            })
        else:
            characteristics.update({
                "soil_types": ["Loamy soil", "Alluvial soil"],
                "texture": "Medium",
                "organic_matter": "Medium",
                "water_retention": "Good",
                "pH_range": "6.5-7.5 (Neutral)",
                "fertility": "Medium to high",
                "additional_features": [
                    "Good nutrient content",
                    "Balanced drainage",
                    "Suitable for most crops",
                    "Moderate mineral content"
                ]
            })

        return characteristics
    

    def get_soil_data(self, lat: float, lon: float, climate: str, rainfall: float) -> Dict:
        try:
            url = f"{self.soil_api_url}?lat={lat}&lng={lon}"
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.soil_api_key
            }
            response = requests.get(url, headers=headers)
            detailed_characteristics = self.determine_detailed_soil_characteristics(lat, lon, climate, rainfall)
            
            return {
     
                "detailed_characteristics": detailed_characteristics
            }
            
        except Exception as e:
            st.warning("Using estimated soil data with detailed characteristics")
           
            detailed_characteristics = self.determine_detailed_soil_characteristics(lat, lon, climate, rainfall)
            return {

                "detailed_characteristics": detailed_characteristics
            }
    def classify_temperature(self,temp: float) -> str:
        """
        Classify temperature ranges in Celsius
        
        Args:
            temp: Temperature in Celsius
        
        Returns:
            Classification string
        """
        if temp < 0:
            return "Freezing"
        elif temp < 10:
            return "Very Cold"
        elif temp < 15:
            return "Cold"
        elif temp < 20:
            return "Cool"
        elif temp < 25:
            return "Moderate"
        elif temp < 30:
            return "Warm"
        elif temp < 35:
            return "Hot"
        else:
            return "Very Hot"

    def classify_humidity(self,humidity: float) -> str:
        """
        Classify relative humidity percentage
        
        Args:
            humidity: Relative humidity percentage (0-100)
        
        Returns:
            Classification string
        """
        if humidity < 20:
            return "Very Dry"
        elif humidity < 30:
            return "Dry"
        elif humidity < 45:
            return "Comfortable Dry"
        elif humidity < 65:
            return "Comfortable"
        elif humidity < 80:
            return "Moderate Humid"
        elif humidity < 90:
            return "Humid"
        else:
            return "Very Humid"

    def classify_solar_radiation(self,radiation: float) -> str:
        """
        Classify solar radiation levels in W/m²
        
        Args:
            radiation: Solar radiation in W/m²
        
        Returns:
            Classification string
        """
        if radiation < 200:
            return "Very Low"
        elif radiation < 400:
            return "Low"
        elif radiation < 600:
            return "Moderate"
        elif radiation < 800:
            return "High"
        elif radiation < 1000:
            return "Very High"
        else:
            return "Extreme"
        
    def analyze_weather_characteristics(self, weather_data: Dict) -> Dict:
            """Analyze detailed weather characteristics"""
            current = weather_data['current']
            temp = current['main']['temp']
            humidity = current['main']['humidity']
            
            # Calculate estimated solar radiation based on latitude, time, and cloud cover
            clouds = current.get('clouds', {}).get('all', 0)
            lat = current.get('coord', {}).get('lat', 0)
            solar_radiation = self.estimate_solar_radiation(lat, clouds)
            
            # Determine dust storm probability based on wind speed and humidity
            wind_speed = current['wind'].get('speed', 0)
            dust_storm_prone = wind_speed > 8 and humidity < 30
            
            return {
                'temperature': {
                    'value': temp,
                    'unit': '°C',
                    'classification': self.classify_temperature(temp)
                },
                'humidity': {
                    'value': humidity,
                    'unit': '%',
                    'classification': self.classify_humidity(humidity)
                },
                'solar_radiation': {
                    'value': solar_radiation,
                    'unit': 'W/m²',
                    'classification': self.classify_solar_radiation(solar_radiation)
                },
                'wind': {
                    'speed': wind_speed,
                    'unit': 'm/s',
                    'dust_storm_probability': 'High' if dust_storm_prone else 'Low'
                },
                'environmental_risks': self.determine_environmental_risks(temp, humidity, wind_speed, solar_radiation)
            }
    def estimate_solar_radiation(self, lat: float, cloud_cover: float) -> float:
            """Estimate solar radiation based on latitude and cloud cover"""
            # Basic estimation formula
            max_radiation = 1000  # Maximum radiation at equator
            latitude_factor = abs(math.cos(math.radians(lat)))
            cloud_factor = 1 - (cloud_cover / 100) * 0.75
            return max_radiation * latitude_factor * cloud_factor

    def determine_environmental_risks(self, temp: float, humidity: float, 
                                    wind_speed: float, solar_radiation: float) -> List[str]:
            """Determine environmental risks based on weather parameters"""
            risks = []
            
            if temp > 35:
                risks.append("High temperature stress")
            if humidity < 30:
                risks.append("High evaporation rate")
            if wind_speed > 8:
                risks.append("Risk of dust storms")
            if solar_radiation > 800:
                risks.append("High solar radiation stress")
                
            return risks

    def determine_detailed_soil_characteristics(self, lat: float, lon: float, 
                                                climate: str, rainfall: float) -> Dict:
            """Determine detailed soil characteristics based on location and climate data"""
            characteristics = {
                "soil_composition": self.determine_soil_composition(climate, rainfall),
                "physical_properties": self.determine_physical_properties(climate, rainfall),
                "chemical_properties": self.determine_chemical_properties(climate, rainfall),
                "water_characteristics": self.determine_water_characteristics(climate, rainfall),
                "fertility_indicators": self.determine_fertility_indicators(climate, rainfall)
            }
            
            return characteristics

    def determine_soil_composition(self, climate: str, rainfall: float) -> Dict:
        """Determine detailed soil composition based on climate and rainfall"""
        if climate.lower() in ['desert', 'clear'] and rainfall < 250:
            return {
                "primary_type": "Desert sandy soils",
                "texture": "Coarse",
                "particle_size": "Large",
                "structure": "Single-grained",
                "color": "Light brown to reddish"
            }
        elif climate.lower() in ['rain', 'thunderstorm'] and rainfall > 2000:
            return {
                "primary_type": "Lateritic soils",
                "texture": "Clay-like",
                "particle_size": "Fine",
                "structure": "Blocky to granular",
                "color": "Deep red to reddish brown"
            }
        elif climate.lower() in ['clouds', 'drizzle'] and 1000 <= rainfall <= 2000:
            return {
                "primary_type": "Forest soils",
                "texture": "Medium to fine",
                "particle_size": "Medium",
                "structure": "Granular",
                "color": "Dark brown to black"
            }
        elif climate.lower() in ['mist', 'fog'] and 500 <= rainfall < 1000:
            return {
                "primary_type": "Prairie soils",
                "texture": "Medium",
                "particle_size": "Medium to fine",
                "structure": "Crumb to blocky",
                "color": "Dark brown"
            }
        else:
            return {
                "primary_type": "Moderate climate soils",
                "texture": "Loamy",
                "particle_size": "Mixed",
                "structure": "Granular to blocky",
                "color": "Brown to dark brown"
            }

    def determine_physical_properties(self, climate: str, rainfall: float) -> Dict:
        """Determine soil physical properties based on climate and rainfall"""
        if climate.lower() in ['desert', 'clear'] and rainfall < 250:
            return {
                "bulk_density": "High",
                "porosity": "High",
                "compaction": "Low",
                "texture_class": "Sandy",
                "structure_stability": "Poor",
                "organic_matter_content": "Very low (<1%)"
            }
        elif climate.lower() in ['rain', 'thunderstorm'] and rainfall > 2000:
            return {
                "bulk_density": "Medium to high",
                "porosity": "Medium",
                "compaction": "Medium",
                "texture_class": "Clay",
                "structure_stability": "Good",
                "organic_matter_content": "High (>4%)"
            }
        elif climate.lower() in ['clouds', 'drizzle'] and 1000 <= rainfall <= 2000:
            return {
                "bulk_density": "Medium",
                "porosity": "High",
                "compaction": "Low to medium",
                "texture_class": "Silty clay loam",
                "structure_stability": "Very good",
                "organic_matter_content": "Very high (>5%)"
            }
        elif climate.lower() in ['mist', 'fog'] and 500 <= rainfall < 1000:
            return {
                "bulk_density": "Medium",
                "porosity": "Medium to high",
                "compaction": "Low",
                "texture_class": "Silt loam",
                "structure_stability": "Good",
                "organic_matter_content": "High (3-4%)"
            }
        else:
            return {
                "bulk_density": "Medium",
                "porosity": "Medium",
                "compaction": "Medium",
                "texture_class": "Loam",
                "structure_stability": "Moderate",
                "organic_matter_content": "Medium (2-3%)"
            }

    def determine_chemical_properties(self, climate: str, rainfall: float) -> Dict:
        """Determine soil chemical properties based on climate and rainfall"""
        if climate.lower() in ['desert', 'clear'] and rainfall < 250:
            return {
                "ph": {
                    "value_range": "8.0-8.8",
                    "classification": "Alkaline"
                },
                "salt_content": {
                    "level": "High",
                    "conductivity": ">4 dS/m"
                },
                "cation_exchange_capacity": "Low",
                "base_saturation": "High",
                "calcium_carbonate": "High"
            }
        elif climate.lower() in ['rain', 'thunderstorm'] and rainfall > 2000:
            return {
                "ph": {
                    "value_range": "4.5-5.5",
                    "classification": "Acidic"
                },
                "salt_content": {
                    "level": "Low",
                    "conductivity": "<2 dS/m"
                },
                "cation_exchange_capacity": "Medium to high",
                "base_saturation": "Low",
                "calcium_carbonate": "Low"
            }
        elif climate.lower() in ['clouds', 'drizzle'] and 1000 <= rainfall <= 2000:
            return {
                "ph": {
                    "value_range": "5.5-6.5",
                    "classification": "Slightly acidic"
                },
                "salt_content": {
                    "level": "Low",
                    "conductivity": "<1 dS/m"
                },
                "cation_exchange_capacity": "High",
                "base_saturation": "Medium",
                "calcium_carbonate": "Low to medium"
            }
        elif climate.lower() in ['mist', 'fog'] and 500 <= rainfall < 1000:
            return {
                "ph": {
                    "value_range": "6.0-7.0",
                    "classification": "Near neutral"
                },
                "salt_content": {
                    "level": "Low to medium",
                    "conductivity": "1-2 dS/m"
                },
                "cation_exchange_capacity": "Medium to high",
                "base_saturation": "Medium to high",
                "calcium_carbonate": "Medium"
            }
        else:
            return {
                "ph": {
                    "value_range": "6.5-7.5",
                    "classification": "Neutral"
                },
                "salt_content": {
                    "level": "Medium",
                    "conductivity": "2-3 dS/m"
                },
                "cation_exchange_capacity": "Medium",
                "base_saturation": "Medium",
                "calcium_carbonate": "Medium"
            }

    def determine_water_characteristics(self, climate: str, rainfall: float) -> Dict:
        """Determine soil water characteristics based on climate and rainfall"""
        if climate.lower() in ['desert', 'clear'] and rainfall < 250:
            return {
                "water_retention": "Poor",
                "drainage": "Excellent",
                "infiltration_rate": "Very high",
                "field_capacity": "Low",
                "wilting_point": "Low",
                "available_water_capacity": "Very low"
            }
        elif climate.lower() in ['rain', 'thunderstorm'] and rainfall > 2000:
            return {
                "water_retention": "High",
                "drainage": "Moderate to poor",
                "infiltration_rate": "Low to medium",
                "field_capacity": "High",
                "wilting_point": "Medium",
                "available_water_capacity": "High"
            }
        elif climate.lower() in ['clouds', 'drizzle'] and 1000 <= rainfall <= 2000:
            return {
                "water_retention": "Very high",
                "drainage": "Moderate",
                "infiltration_rate": "Medium",
                "field_capacity": "Very high",
                "wilting_point": "Medium",
                "available_water_capacity": "Very high"
            }
        elif climate.lower() in ['mist', 'fog'] and 500 <= rainfall < 1000:
            return {
                "water_retention": "Good",
                "drainage": "Good",
                "infiltration_rate": "Medium to high",
                "field_capacity": "Medium to high",
                "wilting_point": "Medium",
                "available_water_capacity": "High"
            }
        else:
            return {
                "water_retention": "Medium",
                "drainage": "Good",
                "infiltration_rate": "Medium",
                "field_capacity": "Medium",
                "wilting_point": "Medium",
                "available_water_capacity": "Medium"
            }

    def determine_fertility_indicators(self, climate: str, rainfall: float) -> Dict:
        """Determine soil fertility indicators based on climate and rainfall"""
        if climate.lower() in ['desert', 'clear'] and rainfall < 250:
            return {
                "fertility_level": "Low",
                "nutrient_availability": {
                    "nitrogen": "Very low",
                    "phosphorus": "Low",
                    "potassium": "Medium",
                    "micronutrients": "Variable"
                },
                "organic_matter_quality": "Poor",
                "biological_activity": "Low",
                "management_requirements": [
                    "Regular nutrient supplementation",
                    "Organic matter addition",
                    "Water conservation practices",
                    "Wind erosion control"
                ]
            }
        elif climate.lower() in ['rain', 'thunderstorm'] and rainfall > 2000:
            return {
                "fertility_level": "Medium",
                "nutrient_availability": {
                    "nitrogen": "Medium to high",
                    "phosphorus": "Low",
                    "potassium": "Low",
                    "micronutrients": "Variable, often deficient"
                },
                "organic_matter_quality": "Good",
                "biological_activity": "High",
                "management_requirements": [
                    "pH management",
                    "Phosphorus supplementation",
                    "Erosion control",
                    "Drainage management"
                ]
            }
        elif climate.lower() in ['clouds', 'drizzle'] and 1000 <= rainfall <= 2000:
            return {
                "fertility_level": "High",
                "nutrient_availability": {
                    "nitrogen": "High",
                    "phosphorus": "Medium to high",
                    "potassium": "Medium",
                    "micronutrients": "Generally adequate"
                },
                "organic_matter_quality": "Excellent",
                "biological_activity": "Very high",
                "management_requirements": [
                    "Balanced fertilization",
                    "Organic matter maintenance",
                    "Soil structure preservation",
                    "Nutrient cycling optimization"
                ]
            }
        elif climate.lower() in ['mist', 'fog'] and 500 <= rainfall < 1000:
            return {
                "fertility_level": "Medium to high",
                "nutrient_availability": {
                    "nitrogen": "Medium",
                    "phosphorus": "Medium",
                    "potassium": "High",
                    "micronutrients": "Adequate"
                },
                "organic_matter_quality": "Good",
                "biological_activity": "Medium to high",
                "management_requirements": [
                    "Moisture conservation",
                    "Balanced fertilization",
                    "Organic matter management",
                    "Soil structure maintenance"
                ]
            }
        else:
            return {
                "fertility_level": "Medium",
                "nutrient_availability": {
                    "nitrogen": "Medium",
                    "phosphorus": "Medium",
                    "potassium": "Medium",
                    "micronutrients": "Generally adequate"
                },
                "organic_matter_quality": "Moderate",
                "biological_activity": "Medium",
                "management_requirements": [
                    "Regular soil testing",
                    "Balanced fertilization",
                    "Organic matter maintenance",
                    "Conservation practices"
                ]
            }
        
    def process_forecast(self, forecast_list: List[Dict]) -> Dict:
        """
        Process 5-day weather forecast data to extract detailed information and trends.

        Args:
            forecast_list: List of forecast data points from OpenWeatherMap API.

        Returns:
            Dictionary containing processed forecast information for 5 days.
        """
        forecast_info = {}
        
        # Group forecasts by date to handle multiple readings per day
        daily_forecasts = {}
        for period in forecast_list:
            timestamp = datetime.fromtimestamp(period['dt'])
            date_str = timestamp.strftime('%Y-%m-%d')
            
            if date_str not in daily_forecasts:
                daily_forecasts[date_str] = []
            daily_forecasts[date_str].append(period)
        
        # Process each day's forecasts
        for date_str, periods in daily_forecasts.items():
            # Calculate daily averages and maximums
            avg_temp = sum(p['main']['temp'] for p in periods) / len(periods)
            max_rain_prob = max(p['pop'] for p in periods)
            
            # Get most common wind direction for the day
            wind_directions = [self.get_cardinal_direction(p['wind'].get('deg', 0)) for p in periods]
            wind_direction = max(set(wind_directions), key=wind_directions.count)
            
            forecast_info[date_str] = {
                'rain_prediction': f"{max_rain_prob * 100:.2f}% chance of rain",
                'temperature_prediction': f"{avg_temp:.2f}°C",
                'wind_direction': wind_direction
            }
        
        return forecast_info



    def get_cardinal_direction(self, degrees: float) -> str:
        """
        Convert wind direction in degrees to a cardinal direction.

        Args:
            degrees: Wind direction in degrees.

        Returns:
            Cardinal direction (e.g., 'N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW').
        """
        directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
        index = round((((degrees + 22.5) % 360) / 45))
        return directions[index]
    
    def analyze_location(self, lat: float, lon: float, address: str) -> Dict:
        """Enhanced location analysis with detailed soil and weather characteristics"""
        weather_data = self.get_weather_data(lat, lon)
        if not weather_data:
            return None

        weather_characteristics = self.analyze_weather_characteristics(weather_data)
        
        current = weather_data['current']
        current_rain = current.get('rain', {}).get('1h', 0)
        climate = current['weather'][0]['main']
        
        soil_data = self.get_soil_data(lat, lon, climate, current_rain)
        soil_characteristics = self.determine_detailed_soil_characteristics(lat, lon, climate, current_rain)
        
        # Get 5-day forecast data
        forecast_list = weather_data['forecast']['list']
        rainfall_forecast = self.process_forecast(forecast_list)

        return {
                    'coordinates': {
                        'latitude': lat,
                        'longitude': lon
                    },
                    'region': address,
                    'weather_analysis': {
                        'current': weather_characteristics,
                        'forecast': rainfall_forecast
                    },
                    'soil_analysis': {
                        'basic_properties': soil_data,
                        'detailed_characteristics': soil_characteristics
                    },
                    'season': self.get_season(datetime.now()),
                    'environmental_conditions': {
                        'climate_type': climate,
                        'risks': weather_characteristics['environmental_risks']
                    }
                }

        

class CropAdvisorLLM:
    def __init__(self):
    #     print("Initializing Mistral model...")
        self.llm = Llama(
            model_path="mistral-7b-instruct-v0.1.Q4_K_M.gguf",
            n_ctx=2048,
            n_threads=os.cpu_count(),
            n_gpu_layers=0,verbose=False
        )
    #     print("Model initialized successfully!")

    def get_recommendations(self, location_data):
        prompt = f"""<s>[INST] You are an agricultural expert. I need specific crop recommendations for this specific location only and conditions.

            Current Conditions:
            Location: {location_data['region']}
            Temperature: {location_data['weather_analysis']['current']['temperature']['value']}°C
            Humidity: {location_data['weather_analysis']['current']['humidity']['value']}%
            Season: {location_data['season']}
            Soil: {location_data['soil_analysis']['basic_properties']['detailed_characteristics']['soil_composition']['texture']}

            Generate 3 specific crop recommendations based on these location conditions. List them in order of suitability.
            TYPE :[category] should be one among fruits,vegetables,cereals,pulses,flowers,leafy vegetables

            First analyze the region's traditional crop patterns, then list 5 most suitable crops considering both regional success 
                            and current conditions. Format each recommendation as:

            1. CROP: [name] | TYPE: [category] | SCORE: [1-100] | REASON: [Include regional significance if applicable]

            Your recommendations: [/INST]

            """

     

        try:
            response = self.llm(
                prompt,
                max_tokens=2048,
                temperature=0.9,  # Lower temperature for more focused output
                top_p=0.9,
                repeat_penalty=1.2,
                stop=["[INST]", "</s>"]
            )

            generated_text = response['choices'][0]['text']
        

            recommendations = self.parse_recommendations("1." + generated_text)
            # end_time = time()
            # print(f"Generation time: {end_time - start_time:.2f} seconds")

            return recommendations

        except Exception as e:
            print(f"Error in generation: {str(e)}")
            return []

    def parse_recommendations(self, text):
        recommendations = []
        current_items = []
        
        # Split by newlines and process each line
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            # Check if line starts with a number and contains a pipe
            if (line.startswith(('1.', '2.', '3.')) or len(current_items) > 0) and '|' in line:
                # Remove the number prefix if it exists
                if line[0].isdigit():
                    line = line.split('.', 1)[1].strip()
                
                # Split by pipes and extract components
                parts = [part.strip() for part in line.split('|')]
                if len(parts) >= 4:
                    rec = {
                        'crop': parts[0],
                        'type': parts[1],
                        'score': parts[2],
                        'reason': parts[3]
                    }
                    recommendations.append(rec)

        return recommendations
    

class YieldAdvisorLLM:
    def __init__(self):
        # Updated static yield data (kg/hectare values from official data)
        self.static_yields = {
            "rice": 2873,
            "wheat": 3615,
            "jowar": 1175,
            "bajra": 1449,
            "maize": 3321,
            "tur": 831,
            "gram": 1224,
            "groundnut": 2179,
            "rapeseed and mustard": 1443,
            "sugarcane": 79000,
            "cotton": 436,
            "jute": 2795,
            "mesta": 2056,
            "potato": 24000,
            "tea": 2042,
            "coffee": 780,
            "rubber": 973
        }
        
        # Convert hectare values to per acre (1 hectare = 2.47105 acres)
        self.static_yields = {crop: yield_value/2.47105 for crop, yield_value in self.static_yields.items()}
        
        try:
            print("Initializing Mistral model...")
            from llama_cpp import Llama
            self.llm = Llama(
                model_path="mistral-7b-instruct-v0.1.Q4_K_M.gguf",
                n_ctx=2048,
                n_threads=4,
                n_gpu_layers=0,
                verbose=False
            )
            print("Model initialized successfully!")
        except Exception as e:
            print(f"Error initializing model: {e}")
            self.llm = None

    def get_recommendations(self, crop: str) -> tuple:
        """Get yield and price recommendations using LLM prompt"""
        print(f"\nGetting recommendations for crop: {crop}")
        
        # First prompt for yield
        yield_prompt = f"""<s>[INST] You are an agricultural specialist. For the crop {crop}, provide its yield per acre for Indian conditions. Return ONLY the numeric yield value in kg/acre.

For reference, some typical Indian crop yields (2023-24):
Rice: 1162 kg/acre
Wheat: 1463 kg/acre
Cotton: 176 kg/acre
Potato: 9713 kg/acre

Respond EXACTLY in this format (just the number):
Yield: XXX[/INST]"""

        # Second prompt for price
        price_prompt = f"""<s>[INST] You are an agricultural market specialist. Provide the current market price per kg for {crop} in India based on recent trends. Return ONLY the numeric price value in rupees per kg.

For reference, some typical crop prices:
Rice: 20-25 Rs/kg
Wheat: 25-30 Rs/kg
Cotton: 60-70 Rs/kg
Potato: 15-20 Rs/kg

Respond EXACTLY in this format (just the number):
Price: XXX[/INST]"""

        try:
            # Get yield prediction
            print(f"Getting yield prediction for {crop}...")
            yield_response = self.llm(
                yield_prompt,
                max_tokens=20,
                temperature=0.1,
                top_p=0.1,
                repeat_penalty=1.2,
                stop=["[INST]", "</s>"]
            )
            
            # Get price prediction
            print(f"Getting price prediction for {crop}...")
            price_response = self.llm(
                price_prompt,
                max_tokens=20,
                temperature=0.1,
                top_p=0.1,
                repeat_penalty=1.2,
                stop=["[INST]", "</s>"]
            )

            # Extract yield value
            yield_text = yield_response['choices'][0]['text'].strip()
            yield_match = re.search(r'Yield:\s*(\d+(?:\.\d+)?)', yield_text)
            
            # Extract price value
            price_text = price_response['choices'][0]['text'].strip()
            price_match = re.search(r'Price:\s*(\d+(?:\.\d+)?)', price_text)

            if yield_match and price_match:
                yield_value = float(yield_match.group(1))
                price_value = float(price_match.group(1))
                print(f"Extracted yield: {yield_value}, price: {price_value}")
                return yield_value, price_value
            else:
                print("Could not extract yield or price value")
                return None, None

        except Exception as e:
            print(f"Error in get_recommendations: {e}")
            return None, None

    def get_yield_prediction(self, crop: str, acres: float) -> Dict[str, Union[str, float]]:
        """Get yield prediction and calculate total income"""
        if not crop:
            return None
            
        crop = crop.lower().strip()
        print(f"\nProcessing crop: {crop}")
        
        try:
            # First check static data for yield
            if crop in self.static_yields:
                yield_per_acre = self.static_yields[crop]
                print(f"Found yield in static data: {yield_per_acre:.2f} kg/acre")
                
                # Only get price from LLM for static yield crops
                price_prompt = f"""<s>[INST] You are an agricultural market specialist. Provide the current market price per kg for {crop} in India based on recent trends. Return ONLY the numeric price value in rupees per kg.

                            For reference, some typical crop prices:
                            Rice: 20-25 Rs/kg
                            Wheat: 25-30 Rs/kg
                            Cotton: 60-70 Rs/kg
                            Potato: 15-20 Rs/kg

                            Respond EXACTLY in this format (just the number):
                            Price: XXX[/INST]"""

                price_response = self.llm(
                    price_prompt,
                    max_tokens=20,
                    temperature=0.9,
                    top_p=0.1,
                    repeat_penalty=1.2,
                    stop=["[INST]", "</s>"]
                )
                
                price_text = price_response['choices'][0]['text'].strip()
                price_match = re.search(r'Price:\s*(\d+(?:\.\d+)?)', price_text)
                
                if not price_match:
                    return {
                        "crop": crop,
                        "acres": acres,
                        "error": "Could not determine price"
                    }
                
                price_per_kg = float(price_match.group(1))
                
            else:
                print(f"Crop {crop} not found in static data")
                
                if self.llm is None:
                    return {
                        "crop": crop,
                        "acres": acres,
                        "error": "LLM model not available"
                    }
                
                # Get both yield and price from LLM for unknown crops
                yield_per_acre, price_per_kg = self.get_recommendations(crop)
                
                if yield_per_acre is None or price_per_kg is None:
                    return {
                        "crop": crop,
                        "acres": acres,
                        "error": "Could not determine yield or price"
                    }

            # Calculate totals
            expected_yield = acres * yield_per_acre
            total_income = expected_yield * price_per_kg
            
            result = {
                "crop": crop,
                "acres": acres,
                "yield_per_acre": yield_per_acre,
                "expected_yield": expected_yield,
                "price_per_kg": price_per_kg,
                "total_income": total_income,
                "unit": "kg"
            }
            print(f"Final result: {result}")
            return result

        except Exception as e:
            print(f"Error in get_yield_prediction: {e}")
            return {
                "crop": crop,
                "acres": acres,
                "error": str(e)
            }
def print_recommendations(recommendations, region):
    print(f"\nRECOMMENDED CROPS FOR {region}")
    print("=" * 60)
    
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. {rec['crop'].upper()}")
            print(f"   Category: {rec['type']}")
            print(f"   Suitability: {rec['score']}")
            print(f"   Reason: {rec['reason']}")
    else:
        print("No recommendations generated. Retrying with different parameters...")
        return False
    return True
        
def render_yield_advisor_tab():
    """Function to render the Yield Advisor tab content"""
    
    # Initialize yield advisor
    yield_advisor = YieldAdvisorLLM()
    
    # Create a container for dynamic crop inputs
    crop_inputs = st.container()
    
    # Initialize all session state variables
    if 'num_crops' not in st.session_state:
        st.session_state.num_crops = 1

    if 'total_yield_value' not in st.session_state:
        st.session_state.total_yield_value = 0.0
        
    if 'total_income_value' not in st.session_state:
        st.session_state.total_income_value = 0.0
    
    # Add/Remove crop buttons
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("Add Crop"):
            st.session_state.num_crops += 1
    with col2:
        if st.button("Remove Crop") and st.session_state.num_crops > 1:
            st.session_state.num_crops -= 1
    
    # Create inputs for each crop
    predictions = []
    
    with crop_inputs:
        for i in range(st.session_state.num_crops):
            col1, col2 = st.columns([2, 1])
            with col1:
                crop = st.text_input(
                    f"Enter Crop Name {i+1}",
                    key=f"crop_{i}",
                    placeholder="e.g., rice, wheat, potato"
                ).strip().lower()
            with col2:
                acres = st.number_input(
                    f"Acres for Crop {i+1}",
                    min_value=0.1,
                    max_value=1000.0,
                    value=1.0,
                    step=0.1,
                    key=f"acres_{i}"
                )
            
            # Only get prediction if crop name is provided
            if crop:
                prediction = yield_advisor.get_yield_prediction(crop, acres)
                if prediction:
                    predictions.append(prediction)
    
    # Add a calculate button
    if st.button("Calculate Yield"):
        if not predictions:
            st.error("Please enter at least one crop name")
        else:
            st.subheader("Yield Predictions")
            
            # Convert predictions to DataFrame for better display
            df = pd.DataFrame(predictions)
            if 'error' in df.columns:
                # Handle cases where some predictions failed
                st.warning("Some predictions could not be calculated")
                df = df[['crop', 'acres', 'error']].fillna('-')
            else:
                # Format the numeric columns
                df['yield_per_acre'] = df['yield_per_acre'].apply(lambda x: f"{x:,.2f} kg/acre")
                df['expected_yield'] = df['expected_yield'].apply(lambda x: f"{x:,.2f} kg")
                df['price_per_kg'] = df['price_per_kg'].apply(lambda x: f"₹{x:,.2f}")
                df['total_income'] = df['total_income'].apply(lambda x: f"₹{x:,.2f}")
                
                # Calculate totals before formatting
                total_area = sum(pred['acres'] for pred in predictions)
                total_yield = sum(pred['expected_yield'] for pred in predictions)
                total_income = sum(pred['total_income'] for pred in predictions)
                
                # Store in session state
                st.session_state.total_yield_value = total_yield
                st.session_state.total_income_value = total_income
                
                # Rename columns for display
                df.columns = ['Crop', 'Acres', 'Yield per Acre', 'Expected Yield', 'Price per kg', 'Total Income', 'Unit']
                df = df.drop('Unit', axis=1)
                
                # Display the formatted DataFrame
                st.dataframe(df, use_container_width=True)
                
                # Display totals
                st.write(f"Total Area: {total_area:,.2f} acres")
                st.write(f"Total Expected Yield: {total_yield:,.2f} kg")
                st.write(f"Total Income: ₹{total_income:,.2f}")
                
                # Add download button for predictions
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download Predictions",
                    data=csv,
                    file_name="yield_predictions.csv",
                    mime="text/csv"
                )
    
    # Add some helpful information
    with st.expander("How to use"):
        st.write("""
        1. Enter the name of each crop you want to analyze
        2. Specify the area in acres for each crop
        3. Click 'Calculate Yield' to get predictions
        4. Add more crops using the 'Add Crop' button if needed
        5. Download your results using the download button
        
        Note: Predictions are based on Indian agricultural data and may vary based on actual conditions.
        """)

def render_profit_dashboard_tab():
    st.header("💰 Profit & Expense Dashboard")
    
    # Initialize session state
    if 'expenses' not in st.session_state:
        st.session_state.expenses = []
    if 'expense_categories' not in st.session_state:
        st.session_state.expense_categories = [
            'Seeds', 'Fertilizers', 'Pesticides', 'Labor', 
            'Equipment', 'Irrigation', 'Transportation', 'Others', 'Cleaning'
        ]
    if 'total_yield_value' not in st.session_state:
        st.session_state.total_yield_value = 0.0
    
    # Get total yield/revenue with the value from yield advisor
    total_yield = st.number_input(
        "Total Revenue/Yield ($)", 
        min_value=0.0, 
        value=st.session_state.total_income_value,
        step=100.0,
        help="This value is automatically populated from your yield predictions. You can adjust it if needed."
    )
    if 'expenses' not in st.session_state:
        st.session_state.expenses = []
    if 'expense_categories' not in st.session_state:
        st.session_state.expense_categories = [
            'Seeds', 'Fertilizers', 'Pesticides', 'Labor', 
            'Equipment', 'Irrigation', 'Transportation', 'Others'
        ]
    
    # Get total yield/revenue
    total_yield = st.number_input("Enter Total Revenue/Yield ($)", 
                                 min_value=0.0, 
                                 value=10000.0, 
                                 step=100.0)
    
    # Add expenses section
    st.subheader("Add Expenses")
    
    # New category input
    new_category = st.text_input("Add New Category (Optional)")
    if new_category and new_category not in st.session_state.expense_categories:
        st.session_state.expense_categories.append(new_category)
        st.success(f"Added new category: {new_category}")
    
    # Expense form
    with st.form("expense_form"):
        st.write("Enter Your Expenses:")
        temp_expenses = []
        
        # Create 5 rows of expense inputs
        for i in range(5):
            col1, col2, col3 = st.columns([2, 2, 2])
            
            with col1:
                name = st.selectbox(
                    f"Category {i+1}",
                    options=[''] + st.session_state.expense_categories,
                    key=f"cat_{i}"
                )
            
            with col2:
                description = st.text_input(
                    f"Description {i+1}",
                    key=f"desc_{i}"
                )
            
            with col3:
                amount = st.number_input(
                    f"Amount {i+1} ($)",
                    min_value=0.0,
                    step=10.0,
                    key=f"amount_{i}"
                )
            
            if name and amount > 0:
                temp_expenses.append({
                    'category': name,
                    'description': description,
                    'amount': amount,
                    'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
        
        submitted = st.form_submit_button("Add Expenses")
        if submitted and temp_expenses:
            st.session_state.expenses.extend(temp_expenses)
            st.success(f"Successfully added {len(temp_expenses)} expenses!")
    
    # Display analytics if there are expenses
    if st.session_state.expenses:
        df_expenses = pd.DataFrame(st.session_state.expenses)
        
        # Calculate metrics
        total_expenses = df_expenses['amount'].sum()
        profit = total_yield - total_expenses
        profit_margin = (profit / total_yield * 100) if total_yield > 0 else 0
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Revenue", f"${total_yield:,.2f}")
        with col2:
            st.metric("Total Expenses", f"${total_expenses:,.2f}", 
                     delta=-total_expenses, 
                     delta_color="inverse")
        with col3:
            st.metric("Net Profit", f"${profit:,.2f}", 
                     delta=f"{profit_margin:.1f}% margin")
        
        # Visualizations
        st.subheader("Financial Analysis")
        
        # Revenue breakdown pie chart
        fig_pie = px.pie(
            values=[profit, total_expenses],
            names=['Profit', 'Expenses'],
            title='Revenue Breakdown',
            color_discrete_sequence=['green', 'red']
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Expenses by category bar chart
        fig_bar = px.bar(
            df_expenses.groupby('category')['amount'].sum().reset_index(),
            x='category',
            y='amount',
            title='Expenses by Category'
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
        # Expense table
        st.subheader("Expense History")
        
        # Category filter
        selected_category = st.selectbox(
            "Filter by Category",
            options=['All'] + list(df_expenses['category'].unique())
        )
        
        # Filter data
        filtered_df = df_expenses if selected_category == 'All' else \
                     df_expenses[df_expenses['category'] == selected_category]
        
        # Display table
        st.dataframe(
            filtered_df.style.format({'amount': '${:,.2f}'}),
            column_config={
                "category": "Category",
                "description": "Description",
                "amount": "Amount",
                "date": "Date Added"
            },
            hide_index=True
        )
        
        # Download button
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download Expense Data",
            data=csv,
            file_name="expenses.csv",
            mime="text/csv"
        )
        
        # Clear button
        if st.button("Clear All Expenses"):
            st.session_state.expenses = []
            st.experimental_rerun()
    
    else:
        st.info("No expenses added yet. Start by adding your expenses using the form above!")

def main():
        st.title("Advanced Soil and Weather Analysis System")

        if 'analysis_result' not in st.session_state:
            st.session_state['analysis_result'] = None
        if 'location_data' not in st.session_state:
            st.session_state['location_data'] = None
        if 'recommendations' not in st.session_state:
            st.session_state['recommendations'] = None
        
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
                tabs = st.tabs(["Location & Weather", "Soil Analysis", "Environmental Risks", "Forecast","Crop Advisor","Yield Advisor","Profit Dashboard"])
                
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
                        

                # Tab 5: Yield Advisor (Now independent)
                with tabs[5]:
                    st.title("Yield Advisor")
                    st.write("Predict crop yields based on official Indian agricultural data")
                    render_yield_advisor_tab()

                with tabs[6]:
                    render_profit_dashboard_tab()

                st.session_state['analysis_result'] = result
            else:
                    st.error("Unable to analyze location. Please try again.")



if __name__ == "__main__":
    main()
