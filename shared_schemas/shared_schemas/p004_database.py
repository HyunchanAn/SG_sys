from pydantic import BaseModel, ConfigDict
from typing import Optional

class AdherendPropertySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    classification: Optional[str] = None
    product_name: Optional[str] = None
    company: Optional[str] = None
    thickness_mm: Optional[float] = None
    roughness_md: Optional[float] = None
    roughness_td: Optional[float] = None
    gloss_md: Optional[float] = None
    gloss_td: Optional[float] = None
    surface_energy_md: Optional[float] = None
    surface_energy_td: Optional[float] = None
    note: Optional[str] = None
