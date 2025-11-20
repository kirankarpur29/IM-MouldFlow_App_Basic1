"""
Geometry processing service for STL files.
Calculates volume, projected area, thickness estimates, etc.
"""
import numpy as np
from stl import mesh
from typing import Dict, Any, Tuple
import io

def process_stl_file(file_content: bytes) -> Dict[str, Any]:
    """
    Process STL file and extract geometric properties.

    Returns volume, projected area, bounding box, and thickness estimates.
    """
    # Load STL from bytes
    stl_mesh = mesh.Mesh.from_file(None, fh=io.BytesIO(file_content))

    # Calculate volume
    volume_mm3 = calculate_volume(stl_mesh)
    volume_cm3 = volume_mm3 / 1000  # Convert to cm³

    # Calculate surface area
    surface_area_mm2 = calculate_surface_area(stl_mesh)
    surface_area_cm2 = surface_area_mm2 / 100  # Convert to cm²

    # Get bounding box
    bbox = get_bounding_box(stl_mesh)

    # Calculate projected area (assuming Z is clamp direction)
    projected_area_mm2 = calculate_projected_area(stl_mesh, axis='z')
    projected_area_cm2 = projected_area_mm2 / 100  # Convert to cm²

    # Estimate thickness
    thickness = estimate_thickness(volume_mm3, surface_area_mm2, bbox)

    return {
        "volume_cm3": round(volume_cm3, 3),
        "surface_area_cm2": round(surface_area_cm2, 2),
        "projected_area_cm2": round(projected_area_cm2, 2),
        "bbox_x": round(bbox['x'], 2),
        "bbox_y": round(bbox['y'], 2),
        "bbox_z": round(bbox['z'], 2),
        "max_thickness": round(thickness['max'], 2),
        "min_thickness": round(thickness['min'], 2),
        "avg_thickness": round(thickness['avg'], 2),
    }


def calculate_volume(stl_mesh) -> float:
    """
    Calculate volume of mesh using signed volume of tetrahedra.
    """
    volume = 0.0
    for triangle in stl_mesh.vectors:
        v0, v1, v2 = triangle
        # Signed volume of tetrahedron formed with origin
        volume += np.dot(v0, np.cross(v1, v2)) / 6.0
    return abs(volume)


def calculate_surface_area(stl_mesh) -> float:
    """
    Calculate total surface area of mesh.
    """
    area = 0.0
    for triangle in stl_mesh.vectors:
        v0, v1, v2 = triangle
        # Area of triangle = 0.5 * |cross product|
        edge1 = v1 - v0
        edge2 = v2 - v0
        area += np.linalg.norm(np.cross(edge1, edge2)) / 2.0
    return area


def get_bounding_box(stl_mesh) -> Dict[str, float]:
    """
    Get bounding box dimensions.
    """
    min_coords = stl_mesh.vectors.min(axis=(0, 1))
    max_coords = stl_mesh.vectors.max(axis=(0, 1))

    return {
        'x': max_coords[0] - min_coords[0],
        'y': max_coords[1] - min_coords[1],
        'z': max_coords[2] - min_coords[2],
        'min': min_coords.tolist(),
        'max': max_coords.tolist()
    }


def calculate_projected_area(stl_mesh, axis: str = 'z') -> float:
    """
    Calculate projected area along specified axis.
    Uses simplified bounding box method for speed.

    For more accurate results, would need 2D projection and polygon union.
    """
    bbox = get_bounding_box(stl_mesh)

    if axis == 'z':
        # Projected area in XY plane
        return bbox['x'] * bbox['y']
    elif axis == 'y':
        return bbox['x'] * bbox['z']
    else:  # axis == 'x'
        return bbox['y'] * bbox['z']


def estimate_thickness(volume_mm3: float, surface_area_mm2: float, bbox: Dict) -> Dict[str, float]:
    """
    Estimate wall thickness from geometry.

    Uses volume/surface area ratio as average thickness estimate.
    Min/max are estimated from bounding box ratios.
    """
    # Average thickness from V/A ratio
    # For a thin shell: V ≈ A × t, so t ≈ V/A
    if surface_area_mm2 > 0:
        avg_thickness = 2 * volume_mm3 / surface_area_mm2
    else:
        avg_thickness = 2.0  # Default

    # Estimate min/max based on typical injection molding ratios
    # These are heuristics - real thickness analysis needs ray casting
    min_thickness = avg_thickness * 0.6
    max_thickness = avg_thickness * 1.8

    # Clamp to reasonable values
    min_thickness = max(0.5, min(min_thickness, 10.0))
    max_thickness = max(min_thickness * 1.2, min(max_thickness, 15.0))
    avg_thickness = max(min_thickness, min(avg_thickness, max_thickness))

    return {
        'min': min_thickness,
        'max': max_thickness,
        'avg': avg_thickness
    }


def process_manual_input(
    length: float,
    width: float,
    height: float,
    avg_thickness: float
) -> Dict[str, Any]:
    """
    Process manual geometry input (no CAD file).
    Creates estimates based on simple box approximation.
    """
    # Estimate volume (hollow box approximation)
    outer_volume = length * width * height

    # Inner dimensions (subtract wall thickness)
    inner_length = max(0, length - 2 * avg_thickness)
    inner_width = max(0, width - 2 * avg_thickness)
    inner_height = max(0, height - 2 * avg_thickness)
    inner_volume = inner_length * inner_width * inner_height

    volume_mm3 = outer_volume - inner_volume
    volume_cm3 = volume_mm3 / 1000

    # Surface area (outer only for simplicity)
    surface_area_mm2 = 2 * (length * width + width * height + height * length)
    surface_area_cm2 = surface_area_mm2 / 100

    # Projected area (largest face)
    projected_area_mm2 = length * width
    projected_area_cm2 = projected_area_mm2 / 100

    # Thickness estimates
    min_thickness = avg_thickness * 0.8
    max_thickness = avg_thickness * 1.5

    return {
        "volume_cm3": round(volume_cm3, 3),
        "surface_area_cm2": round(surface_area_cm2, 2),
        "projected_area_cm2": round(projected_area_cm2, 2),
        "bbox_x": round(length, 2),
        "bbox_y": round(width, 2),
        "bbox_z": round(height, 2),
        "max_thickness": round(max_thickness, 2),
        "min_thickness": round(min_thickness, 2),
        "avg_thickness": round(avg_thickness, 2),
        "note": "Estimated from manual input - No CAD"
    }
