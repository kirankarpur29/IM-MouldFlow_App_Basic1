"""
Heuristic rules for warnings, risk assessment, and feasibility checks.
"""
from typing import List, Dict, Any

def generate_warnings(
    max_thickness_mm: float,
    min_thickness_mm: float,
    flow_ratio: float,
    material_max_ratio: float,
    projected_area_cm2: float,
    tonnage_tons: float,
    cavity_count: int
) -> List[Dict[str, Any]]:
    """
    Generate list of warnings based on analysis parameters.
    Returns warnings with both designer and customer-friendly messages.
    """
    warnings = []

    # Thick section warning
    if max_thickness_mm > 4.0:
        warnings.append({
            "code": "thick_section",
            "severity": "medium",
            "designer_message": f"Max thickness {max_thickness_mm:.1f}mm may cause sink marks and extended cooling time",
            "customer_message": "Thick section detected - may affect surface quality and increase cycle time",
            "recommendation": "Consider coring out thick sections or reducing wall thickness"
        })

    # Very thick section
    if max_thickness_mm > 6.0:
        warnings.append({
            "code": "very_thick_section",
            "severity": "high",
            "designer_message": f"Max thickness {max_thickness_mm:.1f}mm will significantly increase cycle time and risk of voids",
            "customer_message": "Very thick section - will increase production time and may affect part quality",
            "recommendation": "Strongly recommend design review to reduce thickness"
        })

    # Thin section warning
    if min_thickness_mm < 1.0:
        warnings.append({
            "code": "thin_section",
            "severity": "medium",
            "designer_message": f"Min thickness {min_thickness_mm:.1f}mm risks short shots, especially far from gate",
            "customer_message": "Very thin areas may be difficult to fill completely",
            "recommendation": "Ensure gate is positioned near thin sections or increase thickness"
        })

    # Extreme thin section
    if min_thickness_mm < 0.5:
        warnings.append({
            "code": "extreme_thin_section",
            "severity": "high",
            "designer_message": f"Min thickness {min_thickness_mm:.1f}mm is below typical molding limits",
            "customer_message": "Extremely thin areas - high risk of incomplete filling",
            "recommendation": "Increase minimum wall thickness to at least 0.8mm"
        })

    # Thickness variation
    if max_thickness_mm > 0 and min_thickness_mm > 0:
        ratio = max_thickness_mm / min_thickness_mm
        if ratio > 3.0:
            warnings.append({
                "code": "thickness_variation",
                "severity": "medium",
                "designer_message": f"High thickness variation (ratio {ratio:.1f}:1) may cause differential shrinkage",
                "customer_message": "Uneven wall thickness may cause warping or sink marks",
                "recommendation": "Design for uniform wall thickness where possible"
            })

    # Flow length risk
    if flow_ratio > material_max_ratio * 0.9:
        severity = "high" if flow_ratio > material_max_ratio else "medium"
        warnings.append({
            "code": "high_flow_ratio",
            "severity": severity,
            "designer_message": f"Flow L/t ratio {flow_ratio:.0f} exceeds {material_max_ratio:.0f} material limit",
            "customer_message": "Part geometry is challenging for this material - may need additional gates",
            "recommendation": "Consider multiple gates, higher-flow material, or thicker walls"
        })

    # Large projected area
    if projected_area_cm2 > 500:
        warnings.append({
            "code": "large_projected_area",
            "severity": "low",
            "designer_message": f"Large projected area ({projected_area_cm2:.0f} cm²) requires careful venting",
            "customer_message": "Large part size - ensure adequate machine capacity",
            "recommendation": "Plan for adequate venting and balanced fill"
        })

    # High tonnage
    if tonnage_tons > 500:
        warnings.append({
            "code": "high_tonnage",
            "severity": "medium",
            "designer_message": f"High tonnage requirement ({tonnage_tons:.0f}T) - verify machine availability",
            "customer_message": "Requires larger machine - may affect production costs",
            "recommendation": "Confirm machine availability with supplier"
        })

    # Multi-cavity considerations
    if cavity_count > 4:
        warnings.append({
            "code": "multi_cavity",
            "severity": "low",
            "designer_message": f"{cavity_count}-cavity tool requires balanced runner system",
            "customer_message": "Multi-cavity mold - good for high volume production",
            "recommendation": "Ensure balanced runner design for consistent filling"
        })

    return warnings


def calculate_feasibility_score(warnings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate overall feasibility score and status based on warnings.
    """
    # Start with perfect score
    score = 100

    # Deduct points based on warning severity
    severity_deductions = {
        "low": 5,
        "medium": 15,
        "high": 30
    }

    for warning in warnings:
        severity = warning.get("severity", "low")
        score -= severity_deductions.get(severity, 5)

    score = max(0, score)

    # Determine status
    if score >= 70:
        status = "feasible"
        status_message = "Part appears feasible for injection molding"
        color = "green"
    elif score >= 40:
        status = "borderline"
        status_message = "Part is moldable but has some concerns to address"
        color = "amber"
    else:
        status = "not_recommended"
        status_message = "Significant concerns - design review recommended before proceeding"
        color = "red"

    return {
        "score": score,
        "status": status,
        "status_message": status_message,
        "color": color,
        "warning_count": len(warnings),
        "high_severity_count": sum(1 for w in warnings if w.get("severity") == "high")
    }


def estimate_flow_length(bbox_x: float, bbox_y: float, bbox_z: float) -> float:
    """
    Estimate maximum flow length from bounding box.
    Assumes gate at center of largest face.
    """
    # Sort dimensions
    dims = sorted([bbox_x, bbox_y, bbox_z], reverse=True)

    # Flow length is approximately half the diagonal of the two largest dimensions
    # (assuming gate at center)
    flow_length = ((dims[0]/2)**2 + (dims[1]/2)**2)**0.5

    return flow_length
