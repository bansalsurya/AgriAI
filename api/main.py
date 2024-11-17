from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.analyzer import SoilWeatherAnalyzer
from app.recommender import CropAdvisorLLM
from app.yield_analyzer import YieldAdvisorLLM
from app.schemas import LocationData, YieldData
import uvicorn
from typing import List
from utils.state_manager import StateManager

app = FastAPI()
soil_weather_analyzer = SoilWeatherAnalyzer()
advisor = CropAdvisorLLM()
yield_analyzer = YieldAdvisorLLM()

@app.post("/recommend-crops/")
async def recommend_crops(location_data: LocationData):
    data = location_data.dict()
    result = soil_weather_analyzer.analyze_location(data["lat"], data["long"], data["address"])
    recommendations = advisor.get_recommendations(result)
    if not recommendations:
        raise HTTPException(status_code=404, detail="No recommendations found.")
    return {"advisory": result, "recommendations": recommendations}

@app.post("/advisory/")
async def get_advisory(location_data: LocationData):
    data = location_data.dict()
    result = soil_weather_analyzer.analyze_location(data["lat"], data["long"], data["address"])
    return result

@app.post("/yield-prediction/")
async def get_advisory(yield_data: List[YieldData]):
    result = []
    for data in yield_data:
        json_data = data.dict()
        res = yield_analyzer.get_yield_prediction(json_data["crop"],json_data["land"])
        result.append(res)
    return result

@app.get("/")
async def root():
    return {"message": "Welcome to the Crop Recommendation API!"}

# Run the application with `uvicorn main:app --reload`
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
