from typing import Any
from pydantic import BaseModel, Field

class VolumeDiameterRequest(BaseModel):
    volume_ul: float = Field(..., description="액적 부피 (µL)")
    diameter_mm: float = Field(..., description="접촉 직경 (mm)")

class DropletData(BaseModel):
    liquid: str = Field(..., description="용매 이름 (예: Water, Diiodomethane)")
    angle: float = Field(..., description="측정된 접촉각 (도)")

class SFECalculationRequest(BaseModel):
    data: list[DropletData] = Field(..., description="용매별 접촉각 데이터 리스트")

class SFEResponse(BaseModel):
    total_sfe: float = Field(..., description="총 표면 자유 에너지 (mN/m)")
    dispersive: float = Field(..., description="분산 에너지 성분 (mN/m)")
    polar: float = Field(..., description="극성 에너지 성분 (mN/m)")

class AnalysisResponse(BaseModel):
    contact_angle: float = Field(..., description="계산된 접촉각 (도)")
    diagnostics: dict[str, Any] | None = Field(None, description="분석 관련 진단 메타데이터")

class ErrorResponse(BaseModel):
    detail: str
