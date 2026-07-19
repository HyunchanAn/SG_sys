from pydantic import BaseModel

class RoughnessRequest(BaseModel):
    image_data: str

class RoughnessResponse(BaseModel):
    roughness: float
    gloss: float
