"""
Core engineering formulas for mold flow analysis.
All formulas include citations and are designed for transparency.
"""
import math
from typing import Dict, Any

def calculate_clamp_tonnage(
    projected_area_cm2: float,
    cavity_count: int,
    material_pressure_mpa: float,
    safety_factor: float = 1.15
) -> Dict[str, Any]:
    """
    Calculate required clamp tonnage for injection molding.

    Formula: F = A × n × P × SF / 1000
    Where:
        F = Clamp force (metric tons)
        A = Projected area (cm²)
        n = Number of cavities
        P = Cavity pressure (MPa)
        SF = Safety factor

    Reference: Rosato, D.V. "Injection Molding Handbook", 3rd Ed.
    """
    # Calculate force in kN, then convert to metric tons
    force_kn = (projected_area_cm2 * cavity_count * material_pressure_mpa) / 10
    force_tons = force_kn / 9.81

    minimum = force_tons
    recommended = force_tons * safety_factor
    conservative = force_tons * safety_factor * 1.1

    return {
        "minimum": round(minimum, 1),
        "recommended": round(recommended, 1),
        "conservative": round(conservative, 1),
        "formula": "F = (A × n × P) / 10 / 9.81",
        "formula_display": "F = A × n × P × SF",
        "inputs": {
            "projected_area_cm2": projected_area_cm2,
            "cavity_count": cavity_count,
            "material_pressure_mpa": material_pressure_mpa,
            "safety_factor": safety_factor
        },
        "units": "metric tons",
        "reference": "Rosato, Injection Molding Handbook"
    }


def estimate_fill_time(
    part_volume_cm3: float,
    gate_diameter_mm: float,
    material_viscosity_class: str,
    avg_thickness_mm: float
) -> Dict[str, Any]:
    """
    Estimate mold fill time using analytical approximation.

    Based on volumetric flow rate through gate orifice.

    Reference: Adapted from Beaumont, "Runner and Gating Design Handbook"
    """
    # Viscosity multipliers (empirical)
    viscosity_factors = {
        "low": 0.8,    # PP, PE, PS
        "medium": 1.0, # ABS, PA
        "high": 1.3    # PC, POM, PMMA
    }

    # Base flow rate: cm³/s per mm² gate area at standard conditions
    base_flow_rate = 12.0

    gate_area_mm2 = math.pi * (gate_diameter_mm / 2) ** 2
    visc_factor = viscosity_factors.get(material_viscosity_class, 1.0)

    flow_rate = base_flow_rate * gate_area_mm2 / visc_factor

    # Adjust for wall thickness (thinner = more resistance)
    thickness_factor = min(avg_thickness_mm / 2.5, 1.2)  # normalized to 2.5mm
    adjusted_flow_rate = flow_rate * thickness_factor

    fill_time = part_volume_cm3 / adjusted_flow_rate if adjusted_flow_rate > 0 else 0

    return {
        "fill_time_seconds": round(fill_time, 2),
        "flow_rate_cm3_s": round(adjusted_flow_rate, 2),
        "formula": "t = V / Q",
        "confidence": "estimate",
        "note": "Analytical approximation - not FEA simulation",
        "reference": "Beaumont, Runner and Gating Design Handbook"
    }


def estimate_injection_pressure(
    flow_length_mm: float,
    wall_thickness_mm: float,
    material_viscosity_class: str,
    material_base_pressure_mpa: float
) -> Dict[str, Any]:
    """
    Estimate required injection pressure based on flow ratio.

    Uses flow length to thickness ratio with material-specific adjustments.

    Reference: Industry rule-of-thumb correlations
    """
    flow_ratio = flow_length_mm / wall_thickness_mm if wall_thickness_mm > 0 else 0

    # Pressure multipliers based on viscosity
    viscosity_multipliers = {
        "low": 0.85,
        "medium": 1.0,
        "high": 1.25
    }

    mult = viscosity_multipliers.get(material_viscosity_class, 1.0)

    # Pressure increases with flow ratio (simplified model)
    # Base pressure adjusted by log of flow ratio
    ratio_factor = 1 + 0.3 * math.log10(max(flow_ratio / 50, 1))

    pressure = material_base_pressure_mpa * mult * ratio_factor

    return {
        "injection_pressure_mpa": round(pressure, 1),
        "flow_ratio": round(flow_ratio, 0),
        "formula": "P = P_base × k_visc × (1 + 0.3 × log(L/t / 50))",
        "reference": "Industry correlation"
    }


def estimate_cycle_time(
    fill_time: float,
    max_thickness_mm: float,
    material_category: str
) -> Dict[str, Any]:
    """
    Estimate total cycle time.

    Cycle = Fill + Pack + Cool + Mold Open/Close

    Cooling time dominates and scales with thickness squared.

    Reference: Menges, "How to Make Injection Molds", 3rd Ed.
    """
    # Cooling coefficient by material type (s/mm²)
    # Crystalline materials need longer cooling
    cooling_coefficients = {
        "PP": 2.5, "PE": 2.5, "PA": 2.8, "POM": 2.8, "PBT": 2.5,  # Crystalline
        "ABS": 2.0, "PC": 2.2, "PS": 1.8, "PMMA": 2.0, "SAN": 2.0,  # Amorphous
    }

    coeff = cooling_coefficients.get(material_category, 2.2)

    # Cooling time ∝ thickness²
    cooling_time = coeff * (max_thickness_mm ** 2)

    # Pack time typically 20-30% of cooling
    pack_time = cooling_time * 0.25

    # Mold open/close + ejection overhead
    mold_overhead = 3.0  # seconds

    total_cycle = fill_time + pack_time + cooling_time + mold_overhead

    return {
        "fill_time": round(fill_time, 1),
        "pack_time": round(pack_time, 1),
        "cooling_time": round(cooling_time, 1),
        "mold_overhead": mold_overhead,
        "total_cycle": round(total_cycle, 1),
        "formula": "Cooling ≈ k × t²",
        "note": f"Cooling coefficient k={coeff} for {material_category}",
        "reference": "Menges, How to Make Injection Molds"
    }


def check_flow_length_risk(
    flow_length_mm: float,
    wall_thickness_mm: float,
    material_max_ratio: float
) -> Dict[str, Any]:
    """
    Check if flow length to thickness ratio exceeds material capability.

    Reference: Material supplier datasheets
    """
    actual_ratio = flow_length_mm / wall_thickness_mm if wall_thickness_mm > 0 else 0

    if actual_ratio < material_max_ratio * 0.7:
        status = "safe"
        severity = "low"
        message = "Flow length well within material capability"
    elif actual_ratio < material_max_ratio * 0.9:
        status = "borderline"
        severity = "medium"
        message = f"Flow length approaching limit (L/t: {actual_ratio:.0f}, max: {material_max_ratio:.0f})"
    else:
        status = "risk"
        severity = "high"
        message = f"Flow length may exceed material capability (L/t: {actual_ratio:.0f} > {material_max_ratio:.0f})"

    return {
        "status": status,
        "severity": severity,
        "actual_ratio": round(actual_ratio, 0),
        "max_ratio": material_max_ratio,
        "utilization_percent": round(actual_ratio / material_max_ratio * 100, 0) if material_max_ratio > 0 else 0,
        "message": message
    }


def calculate_part_weight(
    volume_cm3: float,
    density_g_cm3: float,
    cavity_count: int = 1
) -> Dict[str, Any]:
    """
    Calculate part weight from volume and material density.
    """
    part_weight = volume_cm3 * density_g_cm3
    total_weight = part_weight * cavity_count

    return {
        "part_weight_grams": round(part_weight, 2),
        "total_shot_weight_grams": round(total_weight, 2),
        "formula": "W = V × ρ",
        "inputs": {
            "volume_cm3": volume_cm3,
            "density_g_cm3": density_g_cm3,
            "cavity_count": cavity_count
        }
    }


def recommend_gate_size(
    part_volume_cm3: float,
    max_thickness_mm: float,
    material_viscosity_class: str
) -> Dict[str, Any]:
    """
    Recommend gate diameter based on part size and material.

    Rule of thumb: Gate diameter = 50-80% of wall thickness
    Adjusted for part volume and material flow characteristics.

    Reference: Industry guidelines
    """
    # Base gate size as percentage of wall thickness
    base_percentage = 0.6

    # Adjust for viscosity
    viscosity_adjustments = {
        "low": -0.05,
        "medium": 0.0,
        "high": 0.1
    }

    # Adjust for volume (larger parts need bigger gates)
    volume_adjustment = min(0.1, part_volume_cm3 / 500 * 0.1)

    percentage = base_percentage + viscosity_adjustments.get(material_viscosity_class, 0) + volume_adjustment
    percentage = min(0.8, max(0.4, percentage))  # Clamp to 40-80%

    gate_diameter = max_thickness_mm * percentage

    # Apply minimum gate size
    gate_diameter = max(gate_diameter, 0.8)  # Minimum 0.8mm

    return {
        "gate_diameter_mm": round(gate_diameter, 2),
        "percentage_of_thickness": round(percentage * 100, 0),
        "rule": "Gate ≈ 50-80% of wall thickness",
        "reference": "Industry guidelines"
    }


def recommend_runner_size(gate_diameter_mm: float) -> Dict[str, Any]:
    """
    Recommend runner diameter based on gate size.

    Rule of thumb: Runner = 1.5-2× gate diameter

    Reference: Beaumont, Runner and Gating Design Handbook
    """
    runner_diameter = gate_diameter_mm * 1.75

    return {
        "runner_diameter_mm": round(runner_diameter, 2),
        "ratio_to_gate": 1.75,
        "rule": "Runner ≈ 1.5-2× gate diameter",
        "reference": "Beaumont, Runner and Gating Design Handbook"
    }
