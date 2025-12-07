# MouldFlow Analysis Web Application - Implementation Plan

## Executive Summary
A web-based mold flow analysis tool providing early-stage feasibility assessment for mold designers and customers, built on open-source stack.

---

## Clarifying Questions (Need Your Input)

Before implementation, please answer these critical questions:

### 1. Material Database Scope
- **Option A**: Generic grades only (e.g., "ABS General Purpose", "PP Homopolymer")
- **Option B**: Include manufacturer-specific grades (e.g., "SABIC Cycolac MG47")
- **Recommended**: Start with Option A, add custom material entry for specific grades

### 2. Machine Library Source
- **Option A**: Generic standard tonnage list (80T, 120T, 180T, 250T, 350T, 500T, 650T, 850T, 1000T)
- **Option B**: Your specific machines/suppliers
- **Question**: Do you have a machine list to provide, or should I use industry-standard ranges?

### 3. Report Tone for Customers
- **Option A**: Very layman-friendly (no equations, plain language only)
- **Option B**: Semi-technical (simplified equations, charts included)
- **Recommended**: Option A with expandable "technical details" sections

### 4. Deployment Context
- **Option A**: Internal tool (authentication required, private hosting)
- **Option B**: Public open-source (anyone can deploy/use)
- **Question**: Which deployment model? This affects auth implementation.

### 5. User Authentication
- **Option A**: No auth (single-user/local use)
- **Option B**: Basic auth (email/password)
- **Option C**: OAuth (Google/GitHub login)
- **Recommended**: Start with Option A, add Option B later

### 6. Specific Standards/Formulas
- Do you have preferred industry formulas for:
  - Clamp tonnage calculation?
  - Flow length ratios?
  - Cycle time estimation?
- Or should I use standard industry rules-of-thumb?

---

## Technology Stack (Optimized for Simplicity)

### Frontend
- **Framework**: React 18 + TypeScript
- **3D Visualization**: Three.js via `@react-three/fiber`
- **UI Components**: Tailwind CSS + shadcn/ui
- **State Management**: Zustand (simpler than Redux)
- **Charts**: Recharts

### Backend
- **Framework**: Python FastAPI
- **Computation**: NumPy, SciPy
- **CAD Processing**: `numpy-stl` for STL, `cadquery` or `OCP` for STEP
- **API Docs**: Auto-generated OpenAPI/Swagger

### Database
- **Primary**: SQLite (MVP) → PostgreSQL (production)
- **ORM**: SQLAlchemy

### Report Generation
- **PDF**: WeasyPrint (HTML/CSS to PDF)
- **Excel**: Pandas + openpyxl

### Deployment
- **Containerization**: Docker + Docker Compose
- **License**: MIT

---

## Database Schema

### Tables

```sql
-- Materials Database
CREATE TABLE materials (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50), -- ABS, PP, PC, etc.
    melt_temp_min FLOAT,
    melt_temp_max FLOAT,
    mold_temp_min FLOAT,
    mold_temp_max FLOAT,
    density FLOAT, -- g/cm³
    shrinkage_min FLOAT, -- %
    shrinkage_max FLOAT,
    viscosity_class VARCHAR(20), -- low/medium/high
    max_flow_length_ratio FLOAT, -- flow length to thickness
    recommended_pressure_min FLOAT, -- MPa
    recommended_pressure_max FLOAT,
    is_custom BOOLEAN DEFAULT FALSE,
    source VARCHAR(100), -- data source citation
    created_at TIMESTAMP DEFAULT NOW()
);

-- Machine Library
CREATE TABLE machines (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    tonnage FLOAT, -- tons
    shot_volume_max FLOAT, -- cm³
    platen_width FLOAT, -- mm
    platen_height FLOAT, -- mm
    tie_bar_spacing_h FLOAT, -- mm
    tie_bar_spacing_v FLOAT, -- mm
    is_custom BOOLEAN DEFAULT FALSE,
    owner_notes TEXT
);

-- Projects
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200),
    customer_name VARCHAR(200),
    designer_name VARCHAR(200),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    status VARCHAR(50) -- draft, analyzed, reported
);

-- Parts (linked to projects)
CREATE TABLE parts (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    name VARCHAR(200),
    -- Geometry data
    file_name VARCHAR(255),
    file_type VARCHAR(10), -- STL, STEP, manual
    volume FLOAT, -- cm³
    projected_area FLOAT, -- cm²
    max_thickness FLOAT, -- mm
    min_thickness FLOAT,
    avg_thickness FLOAT,
    bounding_box_x FLOAT,
    bounding_box_y FLOAT,
    bounding_box_z FLOAT,
    -- Manual input fallback
    manual_length FLOAT,
    manual_width FLOAT,
    manual_height FLOAT,
    -- Stored geometry (binary)
    geometry_data BYTEA
);

-- Analysis Results
CREATE TABLE analyses (
    id SERIAL PRIMARY KEY,
    part_id INTEGER REFERENCES parts(id),
    material_id INTEGER REFERENCES materials(id),
    -- Configuration
    cavity_count INTEGER DEFAULT 1,
    gate_type VARCHAR(50), -- edge, pin, fan, submarine
    gate_location_x FLOAT,
    gate_location_y FLOAT,
    gate_location_z FLOAT,
    gate_diameter FLOAT, -- mm
    runner_diameter FLOAT, -- mm
    -- Results
    fill_time FLOAT, -- seconds
    injection_pressure FLOAT, -- MPa
    clamp_tonnage_min FLOAT,
    clamp_tonnage_recommended FLOAT,
    clamp_tonnage_max FLOAT,
    part_weight FLOAT, -- grams
    cycle_time FLOAT, -- seconds
    -- Feasibility
    feasibility_status VARCHAR(20), -- feasible, borderline, not_recommended
    -- Warnings (JSON array)
    warnings JSONB,
    -- Risk zones (JSON for visualization)
    risk_zones JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Reports
CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    analysis_id INTEGER REFERENCES analyses(id),
    report_type VARCHAR(20), -- designer, customer
    file_path VARCHAR(500),
    generated_at TIMESTAMP DEFAULT NOW()
);
```

---

## Backend API Structure

### Endpoints

```
/api/v1/
├── materials/
│   ├── GET    /                    # List all materials
│   ├── GET    /{id}                # Get material details
│   ├── POST   /                    # Add custom material
│   └── PUT    /{id}                # Update material
│
├── machines/
│   ├── GET    /                    # List all machines
│   ├── GET    /{id}                # Get machine details
│   ├── POST   /                    # Add custom machine
│   ├── GET    /recommend/{tonnage} # Get suitable machines
│   └── PUT    /{id}                # Update machine
│
├── projects/
│   ├── GET    /                    # List projects
│   ├── GET    /{id}                # Get project details
│   ├── POST   /                    # Create project
│   ├── PUT    /{id}                # Update project
│   └── DELETE /{id}                # Delete project
│
├── parts/
│   ├── POST   /upload              # Upload STL/STEP file
│   ├── POST   /manual              # Manual geometry input
│   ├── GET    /{id}                # Get part details
│   ├── GET    /{id}/geometry       # Get 3D geometry data
│   └── PUT    /{id}/orientation    # Update part orientation
│
├── analysis/
│   ├── POST   /                    # Run analysis
│   ├── GET    /{id}                # Get analysis results
│   ├── GET    /{id}/flow-map       # Get flow visualization data
│   └── POST   /{id}/recalculate    # Recalculate with new params
│
└── reports/
    ├── POST   /generate            # Generate report
    ├── GET    /{id}/download       # Download report
    └── GET    /{id}/preview        # Preview report (HTML)
```

### Core Calculation Module Structure

```
/backend/
├── app/
│   ├── main.py                 # FastAPI app entry
│   ├── config.py               # Settings
│   ├── models/                 # SQLAlchemy models
│   ├── schemas/                # Pydantic schemas
│   ├── api/
│   │   └── v1/
│   │       ├── materials.py
│   │       ├── machines.py
│   │       ├── projects.py
│   │       ├── parts.py
│   │       ├── analysis.py
│   │       └── reports.py
│   ├── services/
│   │   ├── geometry_processor.py   # STL/STEP processing
│   │   ├── flow_calculator.py      # Fill time, pressure
│   │   ├── tonnage_calculator.py   # Clamp force
│   │   ├── cycle_calculator.py     # Cycle time
│   │   └── feasibility_checker.py  # Warnings, risk assessment
│   ├── calculations/
│   │   ├── formulas.py             # All engineering formulas
│   │   ├── constants.py            # Industry constants
│   │   └── heuristics.py           # Rule-of-thumb logic
│   └── reports/
│       ├── generator.py
│       ├── templates/
│       │   ├── designer_report.html
│       │   └── customer_report.html
│       └── styles/
```

---

## Frontend Component Structure

```
/frontend/
├── src/
│   ├── App.tsx
│   ├── main.tsx
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── ViewToggle.tsx      # Designer/Customer switch
│   │   ├── viewer/
│   │   │   ├── ModelViewer.tsx     # Three.js 3D viewer
│   │   │   ├── FlowOverlay.tsx     # Flow visualization
│   │   │   └── GateMarker.tsx      # Gate position indicator
│   │   ├── inputs/
│   │   │   ├── FileUpload.tsx      # STL/STEP upload
│   │   │   ├── ManualInput.tsx     # Manual dimensions
│   │   │   ├── MaterialSelect.tsx
│   │   │   ├── GateConfig.tsx      # Gate type, location
│   │   │   └── CavityConfig.tsx
│   │   ├── results/
│   │   │   ├── DesignerResults.tsx # Detailed technical view
│   │   │   ├── CustomerResults.tsx # Simplified summary
│   │   │   ├── TonnageCard.tsx
│   │   │   ├── FeasibilityBadge.tsx # Green/Amber/Red
│   │   │   ├── WarningsList.tsx
│   │   │   └── MachineRecommendations.tsx
│   │   └── reports/
│   │       ├── ReportPreview.tsx
│   │       └── ExportButtons.tsx
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── NewProject.tsx
│   │   ├── Analysis.tsx
│   │   └── Reports.tsx
│   ├── hooks/
│   │   ├── useAnalysis.ts
│   │   └── useProject.ts
│   ├── stores/
│   │   ├── projectStore.ts
│   │   └── uiStore.ts
│   ├── api/
│   │   └── client.ts               # API client
│   └── utils/
│       └── formatters.ts
```

---

## Key Engineering Calculations

### 1. Clamp Tonnage Calculation

```python
def calculate_clamp_tonnage(
    projected_area_cm2: float,
    cavity_count: int,
    material_pressure_mpa: float,
    safety_factor: float = 1.15
) -> dict:
    """
    Formula: Clamp Force = Projected Area × Cavities × Cavity Pressure × Safety Factor

    Reference: Standard industry formula (Rosato, Injection Molding Handbook)
    """
    # Convert to consistent units
    projected_area_mm2 = projected_area_cm2 * 100  # cm² to mm²

    # Calculate force in kN, then convert to tons
    force_kn = (projected_area_mm2 * cavity_count * material_pressure_mpa) / 1000
    force_tons = force_kn / 9.81

    return {
        "minimum": round(force_tons, 1),
        "recommended": round(force_tons * safety_factor, 1),
        "conservative": round(force_tons * safety_factor * 1.1, 1),
        "formula": "F = A × n × P × SF",
        "units": "metric tons"
    }
```

### 2. Fill Time Estimation

```python
def estimate_fill_time(
    part_volume_cm3: float,
    gate_diameter_mm: float,
    material_viscosity_class: str,
    avg_thickness_mm: float
) -> dict:
    """
    Simplified analytical model based on flow rate through gate.

    Reference: Adapted from Moldflow fundamentals
    """
    # Viscosity multipliers (empirical)
    viscosity_factors = {
        "low": 0.8,    # PP, PE
        "medium": 1.0, # ABS, PS
        "high": 1.3    # PC, POM
    }

    # Base flow rate (empirical, cm³/s per mm² gate area)
    base_flow_rate = 15  # cm³/s per mm² at standard conditions

    gate_area_mm2 = 3.14159 * (gate_diameter_mm / 2) ** 2
    flow_rate = base_flow_rate * gate_area_mm2 / viscosity_factors.get(material_viscosity_class, 1.0)

    # Adjust for wall thickness (thinner = slower effective fill)
    thickness_factor = avg_thickness_mm / 2.5  # normalized to 2.5mm standard
    adjusted_flow_rate = flow_rate * min(thickness_factor, 1.2)

    fill_time = part_volume_cm3 / adjusted_flow_rate

    return {
        "fill_time_seconds": round(fill_time, 2),
        "confidence": "estimate",
        "note": "Based on analytical approximation, not FEA simulation"
    }
```

### 3. Cycle Time Estimation

```python
def estimate_cycle_time(
    fill_time: float,
    max_thickness_mm: float,
    material_category: str
) -> dict:
    """
    Cycle Time = Fill + Pack + Cool + Mold Open/Close

    Cooling dominates for most parts.
    Reference: Industry rule-of-thumb
    """
    # Cooling time coefficient by material (seconds per mm² thickness)
    cooling_coefficients = {
        "crystalline": 2.5,    # PP, PE, PA, POM
        "amorphous": 2.0,      # ABS, PC, PS, PMMA
    }

    material_type = "crystalline" if material_category in ["PP", "PE", "PA", "POM"] else "amorphous"

    # Cooling time scales with thickness squared
    cooling_time = cooling_coefficients[material_type] * (max_thickness_mm ** 2)

    # Pack time (typically 20-40% of cooling)
    pack_time = cooling_time * 0.3

    # Mold open/close + ejection (fixed overhead)
    mold_overhead = 3.0  # seconds

    total_cycle = fill_time + pack_time + cooling_time + mold_overhead

    return {
        "fill_time": round(fill_time, 1),
        "pack_time": round(pack_time, 1),
        "cooling_time": round(cooling_time, 1),
        "mold_overhead": mold_overhead,
        "total_cycle": round(total_cycle, 1),
        "formula": "Cooling ≈ k × t²",
        "note": f"Based on {max_thickness_mm}mm max thickness"
    }
```

### 4. Flow Length Risk Check

```python
def check_flow_length_risk(
    flow_length_mm: float,
    wall_thickness_mm: float,
    material_max_ratio: float
) -> dict:
    """
    Check if flow length to thickness ratio exceeds material capability.

    Reference: Material supplier guidelines
    """
    actual_ratio = flow_length_mm / wall_thickness_mm

    if actual_ratio < material_max_ratio * 0.7:
        status = "safe"
        message = "Flow length well within material capability"
    elif actual_ratio < material_max_ratio:
        status = "borderline"
        message = f"Flow length approaching limit (ratio: {actual_ratio:.0f}, max: {material_max_ratio:.0f})"
    else:
        status = "risk"
        message = f"Flow length exceeds recommended ratio for this material"

    return {
        "status": status,
        "actual_ratio": round(actual_ratio, 0),
        "max_ratio": material_max_ratio,
        "message": message
    }
```

---

## Implementation Phases

### Phase 1: Foundation (Week 1-2)
- [ ] Project setup (Docker, FastAPI, React)
- [ ] Database schema implementation
- [ ] Material database seeding (15 common materials)
- [ ] Machine library seeding (standard tonnages)
- [ ] Basic API endpoints for CRUD operations

### Phase 2: Geometry Processing (Week 3)
- [ ] STL file upload and parsing
- [ ] Volume, projected area calculation
- [ ] Thickness analysis (min/max/avg)
- [ ] Bounding box extraction
- [ ] Manual input fallback
- [ ] Three.js 3D viewer integration

### Phase 3: Core Calculations (Week 4-5)
- [ ] Clamp tonnage calculator
- [ ] Fill time estimator
- [ ] Cycle time estimator
- [ ] Flow length risk checker
- [ ] Gate size recommender
- [ ] Machine matching algorithm

### Phase 4: Analysis UI (Week 6)
- [ ] Designer view with all controls
- [ ] Customer view with simplified summary
- [ ] Gate configuration interface
- [ ] Real-time result updates
- [ ] Feasibility badges (Green/Amber/Red)
- [ ] Warning display system

### Phase 5: Visualization (Week 7)
- [ ] 2D flow front approximation
- [ ] Risk zone highlighting
- [ ] Gate location marker
- [ ] Thickness distribution plot

### Phase 6: Reports (Week 8)
- [ ] HTML report templates
- [ ] PDF generation
- [ ] Excel/CSV export
- [ ] Designer vs Customer report variants

### Phase 7: Polish & Documentation (Week 9)
- [ ] Tooltips and help text
- [ ] Formula citations in UI
- [ ] User documentation
- [ ] API documentation
- [ ] Deployment guide

---

## Material Database (Initial Seed Data)

| Material | Category | Melt Temp (°C) | Mold Temp (°C) | Density | Shrinkage (%) | Viscosity | Max L/t Ratio | Pressure (MPa) |
|----------|----------|----------------|----------------|---------|---------------|-----------|---------------|----------------|
| ABS General | ABS | 220-260 | 50-80 | 1.05 | 0.4-0.7 | medium | 150 | 80-120 |
| HIPS | PS | 180-230 | 30-60 | 1.05 | 0.4-0.6 | low | 200 | 60-100 |
| PP Homopolymer | PP | 200-250 | 20-50 | 0.91 | 1.5-2.0 | low | 250 | 60-100 |
| PP Copolymer | PP | 200-250 | 20-50 | 0.91 | 1.3-1.8 | low | 250 | 60-100 |
| HDPE | PE | 200-280 | 20-60 | 0.95 | 2.0-3.0 | low | 200 | 60-100 |
| LDPE | PE | 160-240 | 20-50 | 0.92 | 2.0-3.5 | low | 250 | 50-80 |
| PC General | PC | 280-320 | 80-120 | 1.20 | 0.5-0.7 | high | 100 | 100-150 |
| PC+ABS | PC | 240-280 | 60-90 | 1.15 | 0.5-0.7 | medium | 120 | 80-120 |
| PA6 (Nylon 6) | PA | 240-280 | 60-90 | 1.13 | 1.0-1.5 | medium | 150 | 80-120 |
| PA66 | PA | 270-300 | 70-100 | 1.14 | 1.0-1.5 | medium | 120 | 100-140 |
| POM (Acetal) | POM | 190-210 | 60-90 | 1.41 | 1.8-2.2 | medium | 100 | 80-120 |
| PMMA (Acrylic) | PMMA | 220-260 | 50-80 | 1.18 | 0.4-0.7 | high | 100 | 80-120 |
| PBT | PBT | 240-270 | 60-90 | 1.31 | 1.5-2.0 | medium | 100 | 80-120 |
| TPU | TPE | 180-220 | 30-60 | 1.15 | 1.0-2.0 | medium | 150 | 60-100 |
| SAN | PS | 200-250 | 50-80 | 1.08 | 0.4-0.6 | medium | 120 | 80-120 |

---

## Machine Library (Standard Tonnages)

| Tonnage | Shot Volume (cm³) | Platen W×H (mm) | Typical Use |
|---------|-------------------|-----------------|-------------|
| 80T | 100 | 400×400 | Small parts, low volume |
| 120T | 180 | 450×450 | Small-medium parts |
| 180T | 300 | 500×500 | Medium parts |
| 250T | 500 | 600×600 | Medium parts |
| 350T | 800 | 700×700 | Medium-large parts |
| 500T | 1200 | 800×800 | Large parts |
| 650T | 1800 | 900×900 | Large parts |
| 850T | 2500 | 1000×1000 | Very large parts |
| 1000T | 3500 | 1100×1100 | Very large parts |
| 1300T | 5000 | 1200×1200 | Extra large parts |

---

## Report Structure

### Designer Report Sections
1. Project & Part Information
2. Material Selection (with properties table)
3. Geometry Analysis (volume, area, thickness distribution)
4. Process Parameters (gate, cavities, orientation)
5. **Results**:
   - Fill time & injection pressure
   - Clamp tonnage calculation (with formula)
   - Cycle time breakdown
   - Part weight
6. Machine Recommendations (ranked list)
7. Warnings & Risks (detailed)
8. Flow Visualization Image
9. Appendix: Formulas & References

### Customer Report Sections
1. Executive Summary (1 paragraph)
2. Feasibility Status (large Green/Amber/Red badge)
3. Key Numbers:
   - Recommended machine tonnage
   - Estimated cycle time
   - Part weight
4. Plain-Language Risk Summary
5. Annotated Part Image (gate location, risk zones)
6. Next Steps / Recommendations

---

## Risk/Warning Heuristics

```python
WARNINGS = {
    "thick_section": {
        "condition": "max_thickness > 4mm",
        "designer_msg": "Max thickness {value}mm may cause sink marks and extended cooling",
        "customer_msg": "Thick section detected - may affect surface quality and cycle time"
    },
    "thin_section": {
        "condition": "min_thickness < 1mm",
        "designer_msg": "Min thickness {value}mm risks short shots, especially far from gate",
        "customer_msg": "Very thin areas may be difficult to fill completely"
    },
    "high_flow_ratio": {
        "condition": "flow_length/thickness > material_limit",
        "designer_msg": "Flow L/t ratio {value} exceeds material limit {limit}",
        "customer_msg": "Part geometry challenging for this material - may need gates or material change"
    },
    "large_projected_area": {
        "condition": "projected_area > 500cm²",
        "designer_msg": "Large projected area requires careful venting and balanced fill",
        "customer_msg": "Large part size - needs appropriate machine capacity"
    },
    "high_tonnage": {
        "condition": "tonnage > 500T",
        "designer_msg": "High tonnage requirement - verify platen size and shot capacity",
        "customer_msg": "Requires larger machine - may affect production cost"
    }
}
```

---

## Docker Compose Setup

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - ./uploads:/app/uploads
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/mouldflow
    depends_on:
      - db

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - VITE_API_URL=http://localhost:8000

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=mouldflow
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

---

## Files to Create

```
/
├── README.md
├── LICENSE
├── docker-compose.yml
├── .gitignore
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── api/
│   │   ├── services/
│   │   ├── calculations/
│   │   └── reports/
│   └── tests/
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── stores/
│   │   ├── api/
│   │   └── utils/
│   └── public/
└── docs/
    ├── user-guide.md
    ├── api-reference.md
    └── deployment.md
```

---

## Success Criteria

1. **Functional**
   - Upload STL → see 3D model → get analysis in <5 seconds
   - Generate PDF report with one click
   - Switch between Designer/Customer views seamlessly

2. **Accuracy**
   - Tonnage within ±15% of manual calculation
   - Cycle time within ±20% of typical values
   - All formulas cited and verifiable

3. **Usability**
   - Customer can understand results without training
   - Designer can adjust all key parameters
   - Clear warnings with actionable guidance

4. **Extensibility**
   - Easy to add new materials (form or JSON import)
   - Easy to add new machines
   - API-first for future integrations

---

## Next Steps

1. **Please answer the clarifying questions above** (Section: Clarifying Questions)
2. I will then begin implementation starting with Phase 1
3. Each phase will be committed with clear progress

---

*Document Version: 1.0*
*Created: 2024-11-20*
*Status: Awaiting clarification inputs*
