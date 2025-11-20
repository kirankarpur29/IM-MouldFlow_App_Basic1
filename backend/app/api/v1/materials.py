from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models import Material
from app.schemas import MaterialResponse, MaterialCreate

router = APIRouter()

@router.get("/", response_model=List[MaterialResponse])
async def list_materials(
    category: str = None,
    db: AsyncSession = Depends(get_db)
):
    """List all materials, optionally filtered by category."""
    query = select(Material)
    if category:
        query = query.where(Material.category == category)
    query = query.order_by(Material.category, Material.name)

    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{material_id}", response_model=MaterialResponse)
async def get_material(material_id: int, db: AsyncSession = Depends(get_db)):
    """Get material by ID."""
    material = await db.get(Material, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    return material

@router.post("/", response_model=MaterialResponse)
async def create_material(
    material: MaterialCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add a custom material."""
    db_material = Material(**material.model_dump())
    db.add(db_material)
    await db.commit()
    await db.refresh(db_material)
    return db_material

@router.get("/categories/list")
async def list_categories(db: AsyncSession = Depends(get_db)):
    """Get list of unique material categories."""
    result = await db.execute(
        select(Material.category).distinct().order_by(Material.category)
    )
    return [row[0] for row in result.all()]
