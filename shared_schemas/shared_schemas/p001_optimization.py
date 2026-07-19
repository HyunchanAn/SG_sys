from pydantic import BaseModel, Field

class OptimizeRequest(BaseModel):
    target_properties: dict = Field(..., description="Target properties e.g., {'측정_값': 1200.0, 'Tg': -20.0}")
    fixed_context: dict = Field(default_factory=dict, description="Fixed context e.g. temperature, metal surface")

class OptimizeResponse(BaseModel):
    recipe: dict
    predicted_properties: dict
