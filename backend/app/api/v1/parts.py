from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.models import Part
from app.schemas import ManualGeometryInput
from app.services.geometry_processor import (
    process_stl_file,
    process_step_file,
    process_manual_input,
    generate_flow_visualization,
    generate_risk_zones
)

router = APIRouter()

@router.post("/upload")
async def upload_part(
    file: UploadFile = File(...),
    project_id: int = Form(...),
    name: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """Upload STL or STEP file and extract geometry."""
    filename_lower = file.filename.lower()

    # Validate file type
    if filename_lower.endswith('.stl'):
        file_type = "STL"
    elif filename_lower.endswith(('.step', '.stp')):
        file_type = "STEP"
    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Please upload STL (.stl) or STEP (.step, .stp) files."
        )

    # Read file content
    content = await file.read()

    # Validate file size
    if len(content) > 50 * 1024 * 1024:  # 50MB
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 50MB.")

    # Process geometry based on file type
    try:
        if file_type == "STL":
            geometry = process_stl_file(content)
        else:  # STEP
            geometry = process_step_file(content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing {file_type} file: {str(e)}")

    # Create part record
    part = Part(
        project_id=project_id,
        name=name or file.filename,
        file_name=file.filename,
        file_type=file_type,
        volume=geometry["volume_cm3"],
        projected_area=geometry["projected_area_cm2"],
        surface_area=geometry.get("surface_area_cm2"),
        max_thickness=geometry["max_thickness"],
        min_thickness=geometry["min_thickness"],
        avg_thickness=geometry["avg_thickness"],
        bbox_x=geometry["bbox_x"],
        bbox_y=geometry["bbox_y"],
        bbox_z=geometry["bbox_z"],
        geometry_data=content
    )

    db.add(part)
    await db.commit()
    await db.refresh(part)

    return {
        "id": part.id,
        "name": part.name,
        "file_type": part.file_type,
        "geometry": geometry
    }

@router.post("/manual")
async def create_manual_part(
    project_id: int,
    name: str,
    geometry: ManualGeometryInput,
    db: AsyncSession = Depends(get_db)
):
    """Create part from manual dimension input (no CAD file)."""
    # Process manual input
    processed = process_manual_input(
        geometry.length,
        geometry.width,
        geometry.height,
        geometry.avg_thickness
    )

    # Create part record
    part = Part(
        project_id=project_id,
        name=name,
        file_type="manual",
        volume=processed["volume_cm3"],
        projected_area=processed["projected_area_cm2"],
        surface_area=processed.get("surface_area_cm2"),
        max_thickness=processed["max_thickness"],
        min_thickness=processed["min_thickness"],
        avg_thickness=processed["avg_thickness"],
        bbox_x=processed["bbox_x"],
        bbox_y=processed["bbox_y"],
        bbox_z=processed["bbox_z"],
        manual_length=geometry.length,
        manual_width=geometry.width,
        manual_height=geometry.height,
        manual_thickness=geometry.avg_thickness
    )

    db.add(part)
    await db.commit()
    await db.refresh(part)

    return {
        "id": part.id,
        "name": part.name,
        "file_type": part.file_type,
        "geometry": processed,
        "is_manual": True,
        "note": "Estimated from manual input - No CAD"
    }

@router.get("/{part_id}")
async def get_part(part_id: int, db: AsyncSession = Depends(get_db)):
    """Get part details."""
    part = await db.get(Part, part_id)
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")

    is_manual = part.file_type == "manual"

    return {
        "id": part.id,
        "project_id": part.project_id,
        "name": part.name,
        "file_name": part.file_name,
        "file_type": part.file_type,
        "is_manual": is_manual,
        "geometry": {
            "volume_cm3": part.volume,
            "projected_area_cm2": part.projected_area,
            "surface_area_cm2": part.surface_area,
            "max_thickness": part.max_thickness,
            "min_thickness": part.min_thickness,
            "avg_thickness": part.avg_thickness,
            "bbox_x": part.bbox_x,
            "bbox_y": part.bbox_y,
            "bbox_z": part.bbox_z
        },
        "note": "Estimated from manual input - No CAD" if is_manual else None,
        "created_at": part.created_at
    }

@router.get("/{part_id}/geometry")
async def get_part_geometry_data(part_id: int, db: AsyncSession = Depends(get_db)):
    """Get raw geometry data for 3D visualization."""
    part = await db.get(Part, part_id)
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")

    if not part.geometry_data:
        raise HTTPException(status_code=404, detail="No geometry data available (manual input)")

    # Determine media type based on file type
    if part.file_type == "STEP":
        media_type = "application/step"
    else:
        media_type = "application/octet-stream"

    return Response(
        content=part.geometry_data,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={part.file_name}"}
    )

@router.get("/{part_id}/flow-visualization")
async def get_flow_visualization(
    part_id: int,
    gate_x: Optional[float] = None,
    gate_y: Optional[float] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get flow visualization SVG for a part."""
    part = await db.get(Part, part_id)
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")

    svg = generate_flow_visualization(
        bbox_x=part.bbox_x,
        bbox_y=part.bbox_y,
        gate_x=gate_x,
        gate_y=gate_y
    )

    return Response(
        content=svg,
        media_type="image/svg+xml"
    )

@router.get("/{part_id}/risk-zones")
async def get_risk_zones(
    part_id: int,
    gate_x: Optional[float] = None,
    gate_y: Optional[float] = None,
    material_max_ratio: float = 150,
    db: AsyncSession = Depends(get_db)
):
    """Get risk zone analysis for a part."""
    part = await db.get(Part, part_id)
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")

    risk_zones = generate_risk_zones(
        bbox_x=part.bbox_x,
        bbox_y=part.bbox_y,
        gate_x=gate_x,
        gate_y=gate_y,
        avg_thickness=part.avg_thickness,
        material_max_ratio=material_max_ratio
    )

    return {
        "part_id": part_id,
        "risk_zones": risk_zones
    }

@router.get("/{part_id}/thickness-distribution")
async def get_thickness_distribution(part_id: int, db: AsyncSession = Depends(get_db)):
    """Get thickness distribution data for charts."""
    part = await db.get(Part, part_id)
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")

    # Generate distribution from thickness values
    from app.services.geometry_processor import generate_thickness_distribution
    distribution = generate_thickness_distribution(
        part.min_thickness,
        part.avg_thickness,
        part.max_thickness
    )

    return {
        "part_id": part_id,
        "min_thickness": part.min_thickness,
        "avg_thickness": part.avg_thickness,
        "max_thickness": part.max_thickness,
        "distribution": distribution
    }
