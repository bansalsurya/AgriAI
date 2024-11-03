import requests
from geopy.geocoders import Nominatim
from datetime import datetime
from typing import Dict, Tuple, List
import math
from llama_cpp import Llama
import os
from time import time

def fetch_weather_data(url: str, params: Dict) -> Dict:
    return requests.get(url, params=params).json()

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
            print(f"Error fetching weather data: {e}")
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
            print("Using estimated soil data with detailed characteristics")
           
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