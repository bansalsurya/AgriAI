from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.analyzer import SoilWeatherAnalyzer
from app.recommender import CropAdvisorLLM
from app.schemas import LocationData
import uvicorn

app = FastAPI()
analyzer = SoilWeatherAnalyzer()
advisor = CropAdvisorLLM()

@app.post("/recommend-crops/")
async def recommend_crops(location_data: LocationData):
    data = location_data.dict()
    result = analyzer.analyze_location(data["lat"], data["long"], data["address"])
    recommendations = advisor.get_recommendations(result)
    if not recommendations:
        raise HTTPException(status_code=404, detail="No recommendations found.")
    return recommendations

@app.get("/")
async def root():
    return {"message": "Welcome to the Crop Recommendation API!"}

# Run the application with `uvicorn main:app --reload`
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
