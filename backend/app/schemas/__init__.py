from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime

# Material schemas
class MaterialBase(BaseModel):
    name: str
    manufacturer: Optional[str] = None
    grade: Optional[str] = None
    category: str
    melt_temp_min: float
    melt_temp_max: float
    mold_temp_min: float
    mold_temp_max: float
    density: float
    shrinkage_min: float
    shrinkage_max: float
    mfi: Optional[float] = None
    viscosity_class: str
    max_flow_length_ratio: float
    recommended_pressure_min: float
    recommended_pressure_max: float
    source: Optional[str] = None

class MaterialCreate(MaterialBase):
    is_custom: bool = True

class MaterialResponse(MaterialBase):
    id: int
    is_custom: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Machine schemas
class MachineBase(BaseModel):
    name: str
    manufacturer: Optional[str] = None
    tonnage: float
    shot_volume_max: float
    screw_diameter: Optional[float] = None
    platen_width: float
    platen_height: float
    tie_bar_spacing_h: Optional[float] = None
    tie_bar_spacing_v: Optional[float] = None
    typical_use: Optional[str] = None
    owner_notes: Optional[str] = None

class MachineCreate(MachineBase):
    is_custom: bool = True

class MachineResponse(MachineBase):
    id: int
    is_custom: bool
    created_at: datetime

    class Config:
        from_attributes = True

class MachineRecommendation(BaseModel):
    machine: MachineResponse
    suitability: str  # ideal, acceptable, borderline
    notes: List[str]

# Project schemas
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    customer_name: Optional[str] = None
    designer_name: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    customer_name: Optional[str] = None
    designer_name: Optional[str] = None
    status: Optional[str] = None

class ProjectResponse(ProjectBase):
    id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# Part schemas
class ManualGeometryInput(BaseModel):
    length: float  # mm
    width: float   # mm
    height: float  # mm
    avg_thickness: float  # mm

class PartGeometry(BaseModel):
    volume: float  # cm³
    projected_area: float  # cm²
    surface_area: Optional[float] = None
    max_thickness: float  # mm
    min_thickness: float
    avg_thickness: float
    bbox_x: float
    bbox_y: float
    bbox_z: float

class PartResponse(BaseModel):
    id: int
    project_id: int
    name: Optional[str]
    file_name: Optional[str]
    file_type: str
    geometry: PartGeometry
    created_at: datetime

    class Config:
        from_attributes = True

# Analysis schemas
class AnalysisConfig(BaseModel):
    part_id: int
    material_id: int
    cavity_count: int = 1
    gate_type: str = "edge"  # edge, pin, fan, submarine
    gate_location_x: Optional[float] = None
    gate_location_y: Optional[float] = None
    gate_location_z: Optional[float] = None
    gate_diameter: Optional[float] = None  # Auto-calculate if not provided
    runner_diameter: Optional[float] = None
    safety_factor: float = 1.15

class Warning(BaseModel):
    code: str
    severity: str
    designer_message: str
    customer_message: str
    recommendation: str

class TonnageResult(BaseModel):
    minimum: float
    recommended: float
    conservative: float
    formula: str
    reference: str

class CycleTimeResult(BaseModel):
    fill_time: float
    pack_time: float
    cooling_time: float
    mold_overhead: float
    total_cycle: float
    formula: str
    reference: str

class FeasibilityResult(BaseModel):
    score: int
    status: str
    status_message: str
    color: str
    warning_count: int

class AnalysisResult(BaseModel):
    id: int
    # Config
    cavity_count: int
    gate_type: str
    gate_diameter: float
    runner_diameter: float
    # Fill results
    fill_time: float
    injection_pressure: float
    # Tonnage
    tonnage: TonnageResult
    # Cycle
    cycle_time: CycleTimeResult
    # Weight
    part_weight: float
    shot_weight: float
    # Feasibility
    feasibility: FeasibilityResult
    # Warnings
    warnings: List[Warning]
    # Machine recommendations
    recommended_machines: List[MachineRecommendation]
    # Metadata
    created_at: datetime

    class Config:
        from_attributes = True

# Report schemas
class ReportRequest(BaseModel):
    analysis_id: int
    report_type: str = "designer"  # designer or customer
    format: str = "pdf"  # pdf, html, excel

class ReportResponse(BaseModel):
    id: int
    analysis_id: int
    report_type: str
    format: str
    file_path: str
    generated_at: datetime

    class Config:
        from_attributes = True
