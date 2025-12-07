"""
Geometry processing service for STL and STEP files.
Calculates volume, projected area, thickness estimates, flow visualization.
"""
import numpy as np
from stl import mesh
from typing import Dict, Any, List
import io
import math

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
        "thickness_distribution": thickness.get('distribution', []),
    }


def process_step_file(file_content: bytes) -> Dict[str, Any]:
    """
    Process STEP file and extract geometric properties.

    Uses multiple fallback strategies for robustness.
    """
    # Try method 1: Full cadquery parsing
    try:
        return _process_step_with_cadquery(file_content)
    except Exception as cq_error:
        print(f"CadQuery method failed: {str(cq_error)}")

        # Try method 2: Simple STEP text parsing fallback
        try:
            return _process_step_simple_fallback(file_content)
        except Exception as fallback_error:
            # If both fail, raise a detailed error
            raise RuntimeError(
                f"STEP file processing failed. "
                f"CadQuery error: {str(cq_error)[:100]}. "
                f"Fallback error: {str(fallback_error)[:100]}. "
                f"Please try converting to STL format or use manual input."
            )


def _process_step_with_cadquery(file_content: bytes) -> Dict[str, Any]:
    """
    Full STEP processing with cadquery (requires OpenCASCADE).
    """
    try:
        import cadquery as cq
        from OCP.BRepGProp import BRepGProp
        from OCP.GProp import GProp_GProps
        from OCP.Bnd import Bnd_Box
        from OCP.BRepBndLib import BRepBndLib

        # Use in-memory processing instead of temp files
        import tempfile
        import os

        # Create temp file with proper cleanup
        fd, temp_path = tempfile.mkstemp(suffix='.step', text=False)
        try:
            os.write(fd, file_content)
            os.close(fd)

            # Import STEP file
            result = cq.importers.importStep(temp_path)

            if result is None or result.val() is None:
                raise ValueError("STEP import returned None - file may be corrupted")

            shape = result.val().wrapped

            # Calculate volume
            props = GProp_GProps()
            BRepGProp.VolumeProperties_s(shape, props)
            volume_mm3 = props.Mass()

            if volume_mm3 <= 0:
                raise ValueError(f"Invalid volume calculated: {volume_mm3}")

            volume_cm3 = volume_mm3 / 1000

            # Calculate surface area
            surf_props = GProp_GProps()
            BRepGProp.SurfaceProperties_s(shape, surf_props)
            surface_area_mm2 = surf_props.Mass()
            surface_area_cm2 = surface_area_mm2 / 100

            # Get bounding box
            bbox_obj = Bnd_Box()
            BRepBndLib.Add_s(shape, bbox_obj)
            xmin, ymin, zmin, xmax, ymax, zmax = bbox_obj.Get()

            bbox = {
                'x': abs(xmax - xmin),
                'y': abs(ymax - ymin),
                'z': abs(zmax - zmin),
            }

            # Projected area (XY plane)
            projected_area_mm2 = bbox['x'] * bbox['y']
            projected_area_cm2 = projected_area_mm2 / 100

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
                "thickness_distribution": thickness.get('distribution', []),
            }
        finally:
            # Always cleanup temp file
            try:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
            except:
                pass

    except ImportError as e:
        raise RuntimeError(f"CadQuery not available: {str(e)}. STEP support requires: pip install cadquery")
    except Exception as e:
        raise RuntimeError(f"CadQuery processing failed: {str(e)}")


def _process_step_simple_fallback(file_content: bytes) -> Dict[str, Any]:
    """
    Simple STEP file parsing fallback.
    Extracts basic geometry from STEP text format.
    """
    try:
        # Decode STEP file (it's text format)
        step_text = file_content.decode('utf-8', errors='ignore')

        # Extract bounding box from STEP geometric data
        # STEP files contain coordinate data we can parse
        import re

        # Find all coordinate values in the STEP file
        # Pattern matches numbers in CARTESIAN_POINT definitions
        coord_pattern = r'CARTESIAN_POINT\s*\([^)]*\)\s*,\s*\(([^)]+)\)'
        matches = re.findall(coord_pattern, step_text)

        if not matches:
            # Try alternative pattern
            coord_pattern = r'#\d+\s*=\s*CARTESIAN_POINT\s*\([^)]*,\s*\(([^)]+)\)'
            matches = re.findall(coord_pattern, step_text)

        if not matches:
            raise ValueError("Could not extract coordinates from STEP file")

        # Parse coordinates
        all_coords = []
        for match in matches:
            coords = [float(x.strip()) for x in match.split(',') if x.strip()]
            if len(coords) >= 3:
                all_coords.append(coords[:3])

        if len(all_coords) < 8:
            raise ValueError(f"Insufficient coordinate data found: {len(all_coords)} points")

        # Convert to numpy array
        coords_array = np.array(all_coords)

        # Calculate bounding box
        min_coords = coords_array.min(axis=0)
        max_coords = coords_array.max(axis=0)

        bbox = {
            'x': abs(max_coords[0] - min_coords[0]),
            'y': abs(max_coords[1] - min_coords[1]),
            'z': abs(max_coords[2] - min_coords[2]),
        }

        # Validate bounding box
        if bbox['x'] <= 0 or bbox['y'] <= 0 or bbox['z'] <= 0:
            raise ValueError(f"Invalid bounding box: {bbox}")

        # Estimate volume (assumes roughly rectangular part)
        # This is a rough approximation
        volume_mm3 = bbox['x'] * bbox['y'] * bbox['z'] * 0.4  # 40% fill factor estimate
        volume_cm3 = volume_mm3 / 1000

        # Estimate surface area
        surface_area_mm2 = 2 * (bbox['x'] * bbox['y'] + bbox['y'] * bbox['z'] + bbox['z'] * bbox['x'])
        surface_area_cm2 = surface_area_mm2 / 100

        # Projected area
        projected_area_mm2 = bbox['x'] * bbox['y']
        projected_area_cm2 = projected_area_mm2 / 100

        # Estimate thickness
        avg_thickness = min(bbox['x'], bbox['y'], bbox['z']) * 0.2  # Rough estimate
        thickness = {
            'min': avg_thickness * 0.6,
            'avg': avg_thickness,
            'max': avg_thickness * 1.8,
            'distribution': generate_thickness_distribution(
                avg_thickness * 0.6,
                avg_thickness,
                avg_thickness * 1.8
            )
        }

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
            "thickness_distribution": thickness.get('distribution', []),
            "note": "Estimated from STEP bounding box (simplified parsing)"
        }

    except Exception as e:
        raise RuntimeError(f"Simple STEP parsing failed: {str(e)}")



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
    """
    bbox = get_bounding_box(stl_mesh)

    if axis == 'z':
        return bbox['x'] * bbox['y']
    elif axis == 'y':
        return bbox['x'] * bbox['z']
    else:
        return bbox['y'] * bbox['z']


def estimate_thickness(volume_mm3: float, surface_area_mm2: float, bbox: Dict) -> Dict[str, Any]:
    """
    Estimate wall thickness from geometry.
    """
    # Average thickness from V/A ratio
    if surface_area_mm2 > 0:
        avg_thickness = 2 * volume_mm3 / surface_area_mm2
    else:
        avg_thickness = 2.0

    # Estimate min/max based on typical ratios
    min_thickness = avg_thickness * 0.6
    max_thickness = avg_thickness * 1.8

    # Clamp to reasonable values
    min_thickness = max(0.5, min(min_thickness, 10.0))
    max_thickness = max(min_thickness * 1.2, min(max_thickness, 15.0))
    avg_thickness = max(min_thickness, min(avg_thickness, max_thickness))

    # Generate thickness distribution (simplified histogram)
    distribution = generate_thickness_distribution(min_thickness, avg_thickness, max_thickness)

    return {
        'min': min_thickness,
        'max': max_thickness,
        'avg': avg_thickness,
        'distribution': distribution
    }


def generate_thickness_distribution(min_t: float, avg_t: float, max_t: float) -> List[Dict]:
    """
    Generate a simplified thickness distribution histogram.

    In a real implementation, this would come from ray casting analysis.
    Here we use a normal distribution approximation.
    """
    # Create bins
    num_bins = 8
    bin_width = (max_t - min_t) / num_bins

    # Generate normal distribution centered on average
    std_dev = (max_t - min_t) / 4

    distribution = []
    for i in range(num_bins):
        bin_start = min_t + i * bin_width
        bin_end = bin_start + bin_width
        bin_center = (bin_start + bin_end) / 2

        # Normal distribution probability
        prob = math.exp(-0.5 * ((bin_center - avg_t) / std_dev) ** 2)

        distribution.append({
            "range_start": round(bin_start, 2),
            "range_end": round(bin_end, 2),
            "percentage": round(prob * 100 / num_bins * 2, 1)  # Normalize
        })

    # Normalize to sum to 100
    total = sum(d["percentage"] for d in distribution)
    if total > 0:
        for d in distribution:
            d["percentage"] = round(d["percentage"] * 100 / total, 1)

    return distribution


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

    # Generate distribution
    distribution = generate_thickness_distribution(min_thickness, avg_thickness, max_thickness)

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
        "thickness_distribution": distribution,
        "is_manual": True,
        "note": "Estimated from manual input - No CAD"
    }


def generate_flow_visualization(
    bbox_x: float,
    bbox_y: float,
    gate_x: float = None,
    gate_y: float = None,
    num_contours: int = 8
) -> str:
    """
    Generate SVG visualization of approximate flow fronts.

    Uses radial distance from gate as simplified flow model.
    Returns SVG string.
    """
    # Default gate position to center
    if gate_x is None:
        gate_x = bbox_x / 2
    if gate_y is None:
        gate_y = bbox_y / 2

    # SVG dimensions (scale to fit)
    svg_width = 300
    svg_height = 300
    padding = 20

    # Scale factors
    scale_x = (svg_width - 2 * padding) / bbox_x
    scale_y = (svg_height - 2 * padding) / bbox_y
    scale = min(scale_x, scale_y)

    # Offset to center
    offset_x = padding + (svg_width - 2 * padding - bbox_x * scale) / 2
    offset_y = padding + (svg_height - 2 * padding - bbox_y * scale) / 2

    # Gate position in SVG coordinates
    gate_svg_x = offset_x + gate_x * scale
    gate_svg_y = offset_y + gate_y * scale

    # Maximum flow distance
    max_dist = math.sqrt(bbox_x**2 + bbox_y**2)

    # Generate SVG
    svg_parts = [
        f'<svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">',
        # Background
        f'<rect width="{svg_width}" height="{svg_height}" fill="#f8fafc"/>',
        # Part outline
        f'<rect x="{offset_x}" y="{offset_y}" width="{bbox_x * scale}" height="{bbox_y * scale}" '
        f'fill="none" stroke="#334155" stroke-width="2"/>',
    ]

    # Flow contours (colored rings from gate)
    colors = [
        "#22c55e",  # Green - early fill
        "#84cc16",
        "#eab308",
        "#f97316",
        "#ef4444",  # Red - late fill
        "#dc2626",
        "#b91c1c",
        "#991b1b",
    ]

    for i in range(num_contours, 0, -1):
        radius = (i / num_contours) * max_dist * scale * 0.5
        color = colors[min(i - 1, len(colors) - 1)]
        opacity = 0.3 + (i / num_contours) * 0.4

        svg_parts.append(
            f'<circle cx="{gate_svg_x}" cy="{gate_svg_y}" r="{radius}" '
            f'fill="{color}" fill-opacity="{opacity}" stroke="none"/>'
        )

    # Gate marker
    svg_parts.append(
        f'<circle cx="{gate_svg_x}" cy="{gate_svg_y}" r="6" fill="#1e40af" stroke="#fff" stroke-width="2"/>'
    )

    # Labels
    svg_parts.append(
        f'<text x="{svg_width/2}" y="{svg_height - 5}" text-anchor="middle" '
        f'font-size="10" fill="#64748b">Approximate Flow Pattern (Green=Early, Red=Late)</text>'
    )

    svg_parts.append('</svg>')

    return '\n'.join(svg_parts)


def generate_risk_zones(
    bbox_x: float,
    bbox_y: float,
    gate_x: float = None,
    gate_y: float = None,
    avg_thickness: float = 2.5,
    material_max_ratio: float = 150
) -> List[Dict]:
    """
    Identify potential risk zones based on flow distance.

    Returns list of risk zone coordinates and severity.
    """
    if gate_x is None:
        gate_x = bbox_x / 2
    if gate_y is None:
        gate_y = bbox_y / 2

    risk_zones = []

    # Check corners as potential problem areas
    corners = [
        (0, 0, "bottom-left"),
        (bbox_x, 0, "bottom-right"),
        (0, bbox_y, "top-left"),
        (bbox_x, bbox_y, "top-right")
    ]

    max_safe_distance = avg_thickness * material_max_ratio * 0.7
    max_warning_distance = avg_thickness * material_max_ratio * 0.9

    for x, y, name in corners:
        distance = math.sqrt((x - gate_x)**2 + (y - gate_y)**2)
        flow_ratio = distance / avg_thickness

        if distance > max_warning_distance:
            severity = "high"
        elif distance > max_safe_distance:
            severity = "medium"
        else:
            severity = "low"

        if severity != "low":
            risk_zones.append({
                "location": name,
                "x": x,
                "y": y,
                "distance_mm": round(distance, 1),
                "flow_ratio": round(flow_ratio, 0),
                "severity": severity,
                "message": f"Flow distance {distance:.0f}mm from gate (L/t={flow_ratio:.0f})"
            })

    return risk_zones
