from pydantic import BaseModel

class LocationData(BaseModel):
    lat: str
    long: str
    address: str

class YieldData(BaseModel):
    crop: str
    land: float