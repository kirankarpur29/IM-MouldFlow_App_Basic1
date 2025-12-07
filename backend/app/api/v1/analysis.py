from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Analysis
from app.schemas import AnalysisConfig
from app.services.analysis_service import run_analysis

router = APIRouter()

@router.post("/")
async def create_analysis(
    config: AnalysisConfig,
    db: AsyncSession = Depends(get_db)
):
    """Run mold flow analysis for a part."""
    try:
        gate_location = None
        if config.gate_location_x is not None:
            gate_location = (
                config.gate_location_x,
                config.gate_location_y,
                config.gate_location_z
            )

        result = await run_analysis(
            session=db,
            part_id=config.part_id,
            material_id=config.material_id,
            cavity_count=config.cavity_count,
            gate_type=config.gate_type,
            gate_location=gate_location,
            gate_diameter=config.gate_diameter,
            runner_diameter=config.runner_diameter,
            safety_factor=config.safety_factor
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/{analysis_id}")
async def get_analysis(analysis_id: int, db: AsyncSession = Depends(get_db)):
    """Get analysis results by ID."""
    analysis = await db.get(Analysis, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return {
        "id": analysis.id,
        "part_id": analysis.part_id,
        "material_id": analysis.material_id,
        "cavity_count": analysis.cavity_count,
        "gate_type": analysis.gate_type,
        "gate_diameter": analysis.gate_diameter,
        "runner_diameter": analysis.runner_diameter,
        "fill_time": analysis.fill_time,
        "injection_pressure": analysis.injection_pressure,
        "tonnage": {
            "minimum": analysis.clamp_tonnage_min,
            "recommended": analysis.clamp_tonnage_recommended,
            "conservative": analysis.clamp_tonnage_max
        },
        "cycle_time": {
            "fill_time": analysis.fill_time,
            "pack_time": analysis.pack_time,
            "cooling_time": analysis.cooling_time,
            "total_cycle": analysis.cycle_time
        },
        "part_weight": analysis.part_weight,
        "shot_weight": analysis.shot_weight,
        "feasibility": {
            "score": analysis.feasibility_score,
            "status": analysis.feasibility_status
        },
        "warnings": analysis.warnings,
        "recommended_machines": analysis.recommended_machines,
        "created_at": analysis.created_at
    }

@router.post("/{analysis_id}/recalculate")
async def recalculate_analysis(
    analysis_id: int,
    config: AnalysisConfig,
    db: AsyncSession = Depends(get_db)
):
    """Recalculate analysis with new parameters."""
    # Get existing analysis to verify it exists
    existing = await db.get(Analysis, analysis_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Analysis not found")

    # Run new analysis
    gate_location = None
    if config.gate_location_x is not None:
        gate_location = (
            config.gate_location_x,
            config.gate_location_y,
            config.gate_location_z
        )

    result = await run_analysis(
        session=db,
        part_id=config.part_id,
        material_id=config.material_id,
        cavity_count=config.cavity_count,
        gate_type=config.gate_type,
        gate_location=gate_location,
        gate_diameter=config.gate_diameter,
        runner_diameter=config.runner_diameter,
        safety_factor=config.safety_factor
    )
    return result
