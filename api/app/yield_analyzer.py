import streamlit as st
import pandas as pd
import re
from typing import Dict, Union
from llama_cpp import Llama
import time
from utils.state_manager import StateManager

class YieldAdvisorLLM:
    def __init__(self):
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
        
        # Convert hectare values to per acre
        self.static_yields = {crop: yield_value/2.47105 for crop, yield_value in self.static_yields.items()}
        self.llm = None

    def initialize_llm(self):
        """Initialize the LLM"""
        if self.llm is None:
            try:
                from llama_cpp import Llama  # Ensure this is imported properly
                self.llm = Llama(
                    model_path="mistral-7b-instruct-v0.1.Q4_K_M.gguf",
                    n_ctx=2048,
                    n_threads=4,
                    n_gpu_layers=0,
                    verbose=False
                )
            except Exception as e:
                # Log the error in the API logs
                raise RuntimeError(f"Error initializing LLM: {str(e)}")

    def parse_response(self, response):
        """Parse LLM response to extract yield and price values"""
        try:
            lines = response.strip().split('\n')
            yield_value = None
            price_value = None
            
            for line in lines:
                if line.startswith('Yield:'):
                    yield_value = float(line.replace('Yield:', '').strip())
                elif line.startswith('Price:'):
                    price_value = float(line.replace('Price:', '').strip())
            
            return yield_value, price_value
        except Exception as e:
            print(f"Error parsing response: {str(e)}")
            return None, None

    def get_price_from_llm(self, crop: str) -> float:
        """Get crop price using LLM"""
        if self.llm is None:
            self.initialize_llm()
            if self.llm is None:
                return None

        price_prompt = f"""<s>[INST] You are an agricultural market specialist. Provide the current market price per kg for {crop} in India based on recent trends. Return ONLY the numeric price value in rupees per kg.

        For reference, some typical crop prices:
        Rice: 20-25 Rs/kg
        Wheat: 25-30 Rs/kg
        Cotton: 60-70 Rs/kg
        Potato: 15-20 Rs/kg

        Respond EXACTLY in this format (just the number):
        Price: XXX[/INST]"""

        try:
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
            
            return float(price_match.group(1)) if price_match else None
        except Exception as e:
            print(f"Error getting price: {str(e)}")
            return None

    def get_recommendations(self, crop: str) -> tuple:
        """Get yield and price recommendations using LLM prompt"""
        if self.llm is None:
            self.initialize_llm()
            if self.llm is None:
                return None, None

        combined_prompt = f"""<s>[INST] You are an agricultural specialist. For the crop {crop} in India:
                        1. Provide its yield per acre (in kg/acre)
                        2. Provide its current market price (in Rs/kg)

                        For reference:
                        Typical yields (2023-24):
                        - Rice: 1162 kg/acre
                        - Wheat: 1463 kg/acre
                        - Cotton: 176 kg/acre
                        - Potato: 9713 kg/acre

                        Typical prices:
                        - Rice: 20-25 Rs/kg
                        - Wheat: 25-30 Rs/kg
                        - Cotton: 60-70 Rs/kg
                        - Potato: 15-20 Rs/kg

                        Respond EXACTLY in this format (just the numbers):
                        Yield: XXX
                        Price: XXX[/INST]"""

        try:
            # Add small delay between LLM calls to prevent resource conflicts
            time.sleep(0.1)
            
            response = self.llm(
                combined_prompt,
                max_tokens=20,
                temperature=0.7,
                top_p=0.9,
                repeat_penalty=1.2,
                stop=["[INST]", "</s>"]
            )
            
            response_text = response['choices'][0]['text'].strip()
            return self.parse_response(response_text)
        except Exception as e:
            print(f"Error getting recommendations: {str(e)}")
            return None, None

    def get_yield_prediction(self, crop: str, acres: float) -> Dict[str, Union[str, float]]:
        """Get yield prediction and calculate total income"""
        if not crop:
            return None
            
        crop = crop.lower().strip()
        
        try:
            # First check static data for yield
            if crop in self.static_yields:
                yield_per_acre = self.static_yields[crop]
                price_per_kg = self.get_price_from_llm(crop)
                
                if price_per_kg is None:
                    return {
                        "crop": crop,
                        "acres": acres,
                        "error": "Could not determine price"
                    }
            else:
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
            
            return {
                "crop": crop,
                "acres": acres,
                "yield_per_acre": yield_per_acre,
                "expected_yield": expected_yield,
                "price_per_kg": price_per_kg,
                "total_income": total_income,
                "unit": "kg"
            }

        except Exception as e:
            return {
                "crop": crop,
                "acres": acres,
                "error": str(e)
            }