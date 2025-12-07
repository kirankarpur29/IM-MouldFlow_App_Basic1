from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models import Machine
from app.schemas import MachineResponse, MachineCreate

router = APIRouter()

@router.get("/", response_model=List[MachineResponse])
async def list_machines(db: AsyncSession = Depends(get_db)):
    """List all machines ordered by tonnage."""
    result = await db.execute(
        select(Machine).order_by(Machine.tonnage)
    )
    return result.scalars().all()

@router.get("/{machine_id}", response_model=MachineResponse)
async def get_machine(machine_id: int, db: AsyncSession = Depends(get_db)):
    """Get machine by ID."""
    machine = await db.get(Machine, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    return machine

@router.post("/", response_model=MachineResponse)
async def create_machine(
    machine: MachineCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add a custom machine."""
    db_machine = Machine(**machine.model_dump())
    db.add(db_machine)
    await db.commit()
    await db.refresh(db_machine)
    return db_machine

@router.get("/recommend/{tonnage}")
async def recommend_machines(
    tonnage: float,
    db: AsyncSession = Depends(get_db)
):
    """Get machines suitable for given tonnage requirement."""
    result = await db.execute(
        select(Machine)
        .where(Machine.tonnage >= tonnage * 0.9)
        .where(Machine.tonnage <= tonnage * 2.0)
        .order_by(Machine.tonnage)
        .limit(5)
    )
    return result.scalars().all()
