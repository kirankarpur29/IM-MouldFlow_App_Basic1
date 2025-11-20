from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.models import Part
from app.schemas import ManualGeometryInput
from app.services.geometry_processor import process_stl_file, process_manual_input

router = APIRouter()

@router.post("/upload")
async def upload_part(
    file: UploadFile = File(...),
    project_id: int = Form(...),
    name: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """Upload STL file and extract geometry."""
    # Validate file type
    if not file.filename.lower().endswith('.stl'):
        raise HTTPException(status_code=400, detail="Only STL files supported currently")

    # Read file content
    content = await file.read()

    # Process geometry
    try:
        geometry = process_stl_file(content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing STL: {str(e)}")

    # Create part record
    part = Part(
        project_id=project_id,
        name=name or file.filename,
        file_name=file.filename,
        file_type="STL",
        volume=geometry["volume_cm3"],
        projected_area=geometry["projected_area_cm2"],
        surface_area=geometry["surface_area_cm2"],
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
    """Create part from manual dimension input."""
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
        surface_area=processed["surface_area_cm2"],
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
        "geometry": processed
    }

@router.get("/{part_id}")
async def get_part(part_id: int, db: AsyncSession = Depends(get_db)):
    """Get part details."""
    part = await db.get(Part, part_id)
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")

    return {
        "id": part.id,
        "project_id": part.project_id,
        "name": part.name,
        "file_name": part.file_name,
        "file_type": part.file_type,
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
        "created_at": part.created_at
    }

@router.get("/{part_id}/geometry")
async def get_part_geometry_data(part_id: int, db: AsyncSession = Depends(get_db)):
    """Get raw geometry data for 3D visualization."""
    part = await db.get(Part, part_id)
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")

    if not part.geometry_data:
        raise HTTPException(status_code=404, detail="No geometry data available")

    from fastapi.responses import Response
    return Response(
        content=part.geometry_data,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={part.file_name}"}
    )
