from pydantic import BaseModel, Field

class OptimizeRequest(BaseModel):
    target_properties: dict = Field(..., description="Target properties e.g., {'측정_값': 1200.0, 'Tg': -20.0}")
    fixed_context: dict = Field(default_factory=dict, description="Fixed context e.g. temperature, metal surface")
    initial_recipe: dict | None = Field(default=None, description="Optional initial recipe for warm-start in DE")
    local_search_step: int | None = Field(default=None, description="Step indicating neighborhood search radius schedule in DE")
    target_weights: dict | None = Field(default=None, description="Optional weights for L2 optimization")

class OptimizeResponse(BaseModel):
    recipe: dict
    predicted_properties: dict
    selection_source: str | None = Field(default=None, description="nsga2 | de_fallback_penalty | de_fallback_error | de")
