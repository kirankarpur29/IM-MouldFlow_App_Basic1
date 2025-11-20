"""
Main analysis service that orchestrates all calculations.
"""
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Part, Material, Machine, Analysis
from app.calculations import (
    calculate_clamp_tonnage,
    estimate_fill_time,
    estimate_injection_pressure,
    estimate_cycle_time,
    check_flow_length_risk,
    calculate_part_weight,
    recommend_gate_size,
    recommend_runner_size,
    generate_warnings,
    calculate_feasibility_score,
    estimate_flow_length
)


async def run_analysis(
    session: AsyncSession,
    part_id: int,
    material_id: int,
    cavity_count: int = 1,
    gate_type: str = "edge",
    gate_location: tuple = None,
    gate_diameter: float = None,
    runner_diameter: float = None,
    safety_factor: float = 1.15
) -> Dict[str, Any]:
    """
    Run complete mold flow analysis for a part.
    """
    # Get part and material data
    part = await session.get(Part, part_id)
    material = await session.get(Material, material_id)

    if not part or not material:
        raise ValueError("Part or material not found")

    # Auto-calculate gate size if not provided
    if gate_diameter is None:
        gate_result = recommend_gate_size(
            part.volume,
            part.max_thickness,
            material.viscosity_class
        )
        gate_diameter = gate_result["gate_diameter_mm"]

    # Auto-calculate runner size if not provided
    if runner_diameter is None:
        runner_result = recommend_runner_size(gate_diameter)
        runner_diameter = runner_result["runner_diameter_mm"]

    # Estimate flow length from bounding box
    flow_length = estimate_flow_length(part.bbox_x, part.bbox_y, part.bbox_z)

    # Calculate average material pressure
    avg_pressure = (material.recommended_pressure_min + material.recommended_pressure_max) / 2

    # --- Core Calculations ---

    # 1. Fill time
    fill_result = estimate_fill_time(
        part.volume,
        gate_diameter,
        material.viscosity_class,
        part.avg_thickness
    )
    fill_time = fill_result["fill_time_seconds"]

    # 2. Injection pressure
    pressure_result = estimate_injection_pressure(
        flow_length,
        part.avg_thickness,
        material.viscosity_class,
        avg_pressure
    )
    injection_pressure = pressure_result["injection_pressure_mpa"]

    # 3. Clamp tonnage
    tonnage_result = calculate_clamp_tonnage(
        part.projected_area,
        cavity_count,
        injection_pressure,
        safety_factor
    )

    # 4. Cycle time
    cycle_result = estimate_cycle_time(
        fill_time,
        part.max_thickness,
        material.category
    )

    # 5. Part weight
    weight_result = calculate_part_weight(
        part.volume,
        material.density,
        cavity_count
    )

    # 6. Flow length risk
    flow_risk = check_flow_length_risk(
        flow_length,
        part.avg_thickness,
        material.max_flow_length_ratio
    )

    # --- Generate Warnings ---
    warnings = generate_warnings(
        max_thickness_mm=part.max_thickness,
        min_thickness_mm=part.min_thickness,
        flow_ratio=flow_risk["actual_ratio"],
        material_max_ratio=material.max_flow_length_ratio,
        projected_area_cm2=part.projected_area,
        tonnage_tons=tonnage_result["recommended"],
        cavity_count=cavity_count
    )

    # --- Calculate Feasibility ---
    feasibility = calculate_feasibility_score(warnings)

    # --- Get Machine Recommendations ---
    machines = await get_machine_recommendations(
        session,
        tonnage_result["recommended"],
        weight_result["total_shot_weight_grams"],
        part.bbox_x,
        part.bbox_y
    )

    # --- Save Analysis ---
    analysis = Analysis(
        part_id=part_id,
        material_id=material_id,
        cavity_count=cavity_count,
        gate_type=gate_type,
        gate_location_x=gate_location[0] if gate_location else None,
        gate_location_y=gate_location[1] if gate_location else None,
        gate_location_z=gate_location[2] if gate_location else None,
        gate_diameter=gate_diameter,
        runner_diameter=runner_diameter,
        safety_factor=safety_factor,
        fill_time=fill_time,
        injection_pressure=injection_pressure,
        clamp_tonnage_min=tonnage_result["minimum"],
        clamp_tonnage_recommended=tonnage_result["recommended"],
        clamp_tonnage_max=tonnage_result["conservative"],
        cooling_time=cycle_result["cooling_time"],
        pack_time=cycle_result["pack_time"],
        cycle_time=cycle_result["total_cycle"],
        part_weight=weight_result["part_weight_grams"],
        shot_weight=weight_result["total_shot_weight_grams"],
        feasibility_status=feasibility["status"],
        feasibility_score=feasibility["score"],
        warnings=[w for w in warnings],
        risk_zones=None,  # TODO: Implement flow visualization
        recommended_machines=[m for m in machines]
    )

    session.add(analysis)
    await session.commit()
    await session.refresh(analysis)

    # Return formatted result
    return {
        "id": analysis.id,
        "cavity_count": cavity_count,
        "gate_type": gate_type,
        "gate_diameter": gate_diameter,
        "runner_diameter": runner_diameter,
        "fill_time": fill_time,
        "injection_pressure": injection_pressure,
        "tonnage": tonnage_result,
        "cycle_time": cycle_result,
        "part_weight": weight_result["part_weight_grams"],
        "shot_weight": weight_result["total_shot_weight_grams"],
        "feasibility": feasibility,
        "warnings": warnings,
        "recommended_machines": machines,
        "created_at": analysis.created_at
    }


async def get_machine_recommendations(
    session: AsyncSession,
    required_tonnage: float,
    shot_weight: float,
    part_width: float,
    part_height: float
) -> List[Dict[str, Any]]:
    """
    Get list of suitable machines for the analysis.
    """
    # Convert shot weight to volume (approximate, using 1.0 density)
    shot_volume = shot_weight / 1.0  # cm³

    # Get all machines ordered by tonnage
    result = await session.execute(
        select(Machine).order_by(Machine.tonnage)
    )
    all_machines = result.scalars().all()

    recommendations = []

    for machine in all_machines:
        notes = []
        suitability = "ideal"

        # Check tonnage
        if machine.tonnage < required_tonnage * 0.9:
            continue  # Too small, skip
        elif machine.tonnage < required_tonnage:
            suitability = "borderline"
            notes.append(f"Tonnage {machine.tonnage}T is slightly below recommended {required_tonnage:.0f}T")
        elif machine.tonnage > required_tonnage * 2:
            if len(recommendations) >= 3:
                continue  # Skip if we have enough and this is too big
            suitability = "acceptable"
            notes.append(f"Machine may be oversized for this part")

        # Check shot volume
        if machine.shot_volume_max < shot_volume:
            suitability = "borderline"
            notes.append(f"Shot volume {machine.shot_volume_max}cm³ may be insufficient")
        elif machine.shot_volume_max < shot_volume * 1.3:
            if suitability == "ideal":
                suitability = "acceptable"
            notes.append(f"Shot volume near limit")

        # Check platen size (simplified)
        if machine.platen_width < part_width * 1.5 or machine.platen_height < part_height * 1.5:
            suitability = "borderline"
            notes.append(f"Platen size may be tight for mold")

        if not notes:
            notes.append("Good match for tonnage, shot volume, and platen size")

        recommendations.append({
            "machine": {
                "id": machine.id,
                "name": machine.name,
                "tonnage": machine.tonnage,
                "shot_volume_max": machine.shot_volume_max,
                "platen_width": machine.platen_width,
                "platen_height": machine.platen_height,
                "typical_use": machine.typical_use
            },
            "suitability": suitability,
            "notes": notes
        })

        # Limit to 5 recommendations
        if len(recommendations) >= 5:
            break

    # Sort by suitability
    suitability_order = {"ideal": 0, "acceptable": 1, "borderline": 2}
    recommendations.sort(key=lambda x: suitability_order.get(x["suitability"], 3))

    return recommendations[:3]  # Return top 3
