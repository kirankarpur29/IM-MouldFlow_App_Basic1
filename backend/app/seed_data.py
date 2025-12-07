"""
Seed data for materials and machines database.
Includes manufacturer-specific grades.
"""

MATERIALS_SEED = [
    # ABS grades
    {
        "name": "ABS General Purpose",
        "manufacturer": "Generic",
        "grade": "GP",
        "category": "ABS",
        "melt_temp_min": 220, "melt_temp_max": 260,
        "mold_temp_min": 50, "mold_temp_max": 80,
        "density": 1.05,
        "shrinkage_min": 0.4, "shrinkage_max": 0.7,
        "mfi": 20,
        "viscosity_class": "medium",
        "max_flow_length_ratio": 150,
        "recommended_pressure_min": 80, "recommended_pressure_max": 120,
        "source": "Generic material datasheet"
    },
    {
        "name": "SABIC Cycolac MG47",
        "manufacturer": "SABIC",
        "grade": "Cycolac MG47",
        "category": "ABS",
        "melt_temp_min": 230, "melt_temp_max": 260,
        "mold_temp_min": 60, "mold_temp_max": 80,
        "density": 1.05,
        "shrinkage_min": 0.4, "shrinkage_max": 0.6,
        "mfi": 18,
        "viscosity_class": "medium",
        "max_flow_length_ratio": 160,
        "recommended_pressure_min": 80, "recommended_pressure_max": 110,
        "source": "SABIC technical datasheet"
    },
    {
        "name": "LG ABS HI121H",
        "manufacturer": "LG Chem",
        "grade": "HI121H",
        "category": "ABS",
        "melt_temp_min": 220, "melt_temp_max": 250,
        "mold_temp_min": 50, "mold_temp_max": 70,
        "density": 1.04,
        "shrinkage_min": 0.4, "shrinkage_max": 0.7,
        "mfi": 21,
        "viscosity_class": "medium",
        "max_flow_length_ratio": 150,
        "recommended_pressure_min": 75, "recommended_pressure_max": 115,
        "source": "LG Chem technical datasheet"
    },
    # PP grades
    {
        "name": "PP Homopolymer",
        "manufacturer": "Generic",
        "grade": "Homo",
        "category": "PP",
        "melt_temp_min": 200, "melt_temp_max": 250,
        "mold_temp_min": 20, "mold_temp_max": 50,
        "density": 0.91,
        "shrinkage_min": 1.5, "shrinkage_max": 2.0,
        "mfi": 12,
        "viscosity_class": "low",
        "max_flow_length_ratio": 250,
        "recommended_pressure_min": 60, "recommended_pressure_max": 100,
        "source": "Generic material datasheet"
    },
    {
        "name": "SABIC PP 500P",
        "manufacturer": "SABIC",
        "grade": "500P",
        "category": "PP",
        "melt_temp_min": 200, "melt_temp_max": 240,
        "mold_temp_min": 20, "mold_temp_max": 50,
        "density": 0.905,
        "shrinkage_min": 1.5, "shrinkage_max": 2.0,
        "mfi": 3,
        "viscosity_class": "medium",
        "max_flow_length_ratio": 200,
        "recommended_pressure_min": 70, "recommended_pressure_max": 110,
        "source": "SABIC technical datasheet"
    },
    {
        "name": "LyondellBasell Moplen HP500N",
        "manufacturer": "LyondellBasell",
        "grade": "Moplen HP500N",
        "category": "PP",
        "melt_temp_min": 200, "melt_temp_max": 250,
        "mold_temp_min": 20, "mold_temp_max": 50,
        "density": 0.90,
        "shrinkage_min": 1.4, "shrinkage_max": 1.9,
        "mfi": 12,
        "viscosity_class": "low",
        "max_flow_length_ratio": 260,
        "recommended_pressure_min": 60, "recommended_pressure_max": 100,
        "source": "LyondellBasell technical datasheet"
    },
    # PC grades
    {
        "name": "PC General Purpose",
        "manufacturer": "Generic",
        "grade": "GP",
        "category": "PC",
        "melt_temp_min": 280, "melt_temp_max": 320,
        "mold_temp_min": 80, "mold_temp_max": 120,
        "density": 1.20,
        "shrinkage_min": 0.5, "shrinkage_max": 0.7,
        "mfi": 10,
        "viscosity_class": "high",
        "max_flow_length_ratio": 100,
        "recommended_pressure_min": 100, "recommended_pressure_max": 150,
        "source": "Generic material datasheet"
    },
    {
        "name": "Covestro Makrolon 2405",
        "manufacturer": "Covestro",
        "grade": "Makrolon 2405",
        "category": "PC",
        "melt_temp_min": 280, "melt_temp_max": 320,
        "mold_temp_min": 80, "mold_temp_max": 110,
        "density": 1.20,
        "shrinkage_min": 0.5, "shrinkage_max": 0.7,
        "mfi": 10,
        "viscosity_class": "high",
        "max_flow_length_ratio": 100,
        "recommended_pressure_min": 100, "recommended_pressure_max": 140,
        "source": "Covestro technical datasheet"
    },
    {
        "name": "SABIC Lexan 141R",
        "manufacturer": "SABIC",
        "grade": "Lexan 141R",
        "category": "PC",
        "melt_temp_min": 280, "melt_temp_max": 310,
        "mold_temp_min": 80, "mold_temp_max": 120,
        "density": 1.20,
        "shrinkage_min": 0.5, "shrinkage_max": 0.7,
        "mfi": 10.5,
        "viscosity_class": "high",
        "max_flow_length_ratio": 105,
        "recommended_pressure_min": 100, "recommended_pressure_max": 145,
        "source": "SABIC technical datasheet"
    },
    # PA (Nylon) grades
    {
        "name": "PA6 General",
        "manufacturer": "Generic",
        "grade": "PA6",
        "category": "PA",
        "melt_temp_min": 240, "melt_temp_max": 280,
        "mold_temp_min": 60, "mold_temp_max": 90,
        "density": 1.13,
        "shrinkage_min": 1.0, "shrinkage_max": 1.5,
        "mfi": 35,
        "viscosity_class": "medium",
        "max_flow_length_ratio": 150,
        "recommended_pressure_min": 80, "recommended_pressure_max": 120,
        "source": "Generic material datasheet"
    },
    {
        "name": "BASF Ultramid B3S",
        "manufacturer": "BASF",
        "grade": "Ultramid B3S",
        "category": "PA",
        "melt_temp_min": 250, "melt_temp_max": 280,
        "mold_temp_min": 70, "mold_temp_max": 90,
        "density": 1.13,
        "shrinkage_min": 0.8, "shrinkage_max": 1.5,
        "mfi": 100,
        "viscosity_class": "low",
        "max_flow_length_ratio": 180,
        "recommended_pressure_min": 70, "recommended_pressure_max": 110,
        "source": "BASF technical datasheet"
    },
    {
        "name": "DuPont Zytel 101L",
        "manufacturer": "DuPont",
        "grade": "Zytel 101L",
        "category": "PA",
        "melt_temp_min": 270, "melt_temp_max": 295,
        "mold_temp_min": 70, "mold_temp_max": 100,
        "density": 1.14,
        "shrinkage_min": 1.0, "shrinkage_max": 1.5,
        "mfi": 45,
        "viscosity_class": "medium",
        "max_flow_length_ratio": 140,
        "recommended_pressure_min": 80, "recommended_pressure_max": 120,
        "source": "DuPont technical datasheet"
    },
    # Other common materials
    {
        "name": "HIPS",
        "manufacturer": "Generic",
        "grade": "High Impact PS",
        "category": "PS",
        "melt_temp_min": 180, "melt_temp_max": 230,
        "mold_temp_min": 30, "mold_temp_max": 60,
        "density": 1.05,
        "shrinkage_min": 0.4, "shrinkage_max": 0.6,
        "mfi": 8,
        "viscosity_class": "low",
        "max_flow_length_ratio": 200,
        "recommended_pressure_min": 60, "recommended_pressure_max": 100,
        "source": "Generic material datasheet"
    },
    {
        "name": "HDPE",
        "manufacturer": "Generic",
        "grade": "High Density",
        "category": "PE",
        "melt_temp_min": 200, "melt_temp_max": 280,
        "mold_temp_min": 20, "mold_temp_max": 60,
        "density": 0.95,
        "shrinkage_min": 2.0, "shrinkage_max": 3.0,
        "mfi": 8,
        "viscosity_class": "low",
        "max_flow_length_ratio": 200,
        "recommended_pressure_min": 60, "recommended_pressure_max": 100,
        "source": "Generic material datasheet"
    },
    {
        "name": "POM (Acetal)",
        "manufacturer": "Generic",
        "grade": "Copolymer",
        "category": "POM",
        "melt_temp_min": 190, "melt_temp_max": 210,
        "mold_temp_min": 60, "mold_temp_max": 90,
        "density": 1.41,
        "shrinkage_min": 1.8, "shrinkage_max": 2.2,
        "mfi": 9,
        "viscosity_class": "medium",
        "max_flow_length_ratio": 100,
        "recommended_pressure_min": 80, "recommended_pressure_max": 120,
        "source": "Generic material datasheet"
    },
    {
        "name": "DuPont Delrin 500P",
        "manufacturer": "DuPont",
        "grade": "Delrin 500P",
        "category": "POM",
        "melt_temp_min": 200, "melt_temp_max": 220,
        "mold_temp_min": 80, "mold_temp_max": 100,
        "density": 1.42,
        "shrinkage_min": 1.9, "shrinkage_max": 2.1,
        "mfi": 14,
        "viscosity_class": "low",
        "max_flow_length_ratio": 120,
        "recommended_pressure_min": 75, "recommended_pressure_max": 115,
        "source": "DuPont technical datasheet"
    },
    {
        "name": "PC+ABS Blend",
        "manufacturer": "Generic",
        "grade": "Blend",
        "category": "PC",
        "melt_temp_min": 240, "melt_temp_max": 280,
        "mold_temp_min": 60, "mold_temp_max": 90,
        "density": 1.15,
        "shrinkage_min": 0.5, "shrinkage_max": 0.7,
        "mfi": 15,
        "viscosity_class": "medium",
        "max_flow_length_ratio": 120,
        "recommended_pressure_min": 80, "recommended_pressure_max": 120,
        "source": "Generic material datasheet"
    },
    {
        "name": "Covestro Bayblend T65 XF",
        "manufacturer": "Covestro",
        "grade": "Bayblend T65 XF",
        "category": "PC",
        "melt_temp_min": 250, "melt_temp_max": 280,
        "mold_temp_min": 60, "mold_temp_max": 80,
        "density": 1.13,
        "shrinkage_min": 0.5, "shrinkage_max": 0.7,
        "mfi": 17,
        "viscosity_class": "medium",
        "max_flow_length_ratio": 130,
        "recommended_pressure_min": 80, "recommended_pressure_max": 115,
        "source": "Covestro technical datasheet"
    },
    {
        "name": "PMMA (Acrylic)",
        "manufacturer": "Generic",
        "grade": "General",
        "category": "PMMA",
        "melt_temp_min": 220, "melt_temp_max": 260,
        "mold_temp_min": 50, "mold_temp_max": 80,
        "density": 1.18,
        "shrinkage_min": 0.4, "shrinkage_max": 0.7,
        "mfi": 8,
        "viscosity_class": "high",
        "max_flow_length_ratio": 100,
        "recommended_pressure_min": 80, "recommended_pressure_max": 120,
        "source": "Generic material datasheet"
    },
    {
        "name": "PBT",
        "manufacturer": "Generic",
        "grade": "Unreinforced",
        "category": "PBT",
        "melt_temp_min": 240, "melt_temp_max": 270,
        "mold_temp_min": 60, "mold_temp_max": 90,
        "density": 1.31,
        "shrinkage_min": 1.5, "shrinkage_max": 2.0,
        "mfi": 15,
        "viscosity_class": "medium",
        "max_flow_length_ratio": 100,
        "recommended_pressure_min": 80, "recommended_pressure_max": 120,
        "source": "Generic material datasheet"
    },
]

MACHINES_SEED = [
    {
        "name": "80T Standard",
        "manufacturer": "Generic",
        "tonnage": 80,
        "shot_volume_max": 100,
        "screw_diameter": 32,
        "platen_width": 400,
        "platen_height": 400,
        "tie_bar_spacing_h": 320,
        "tie_bar_spacing_v": 320,
        "typical_use": "Small parts, low volume"
    },
    {
        "name": "120T Standard",
        "manufacturer": "Generic",
        "tonnage": 120,
        "shot_volume_max": 180,
        "screw_diameter": 36,
        "platen_width": 450,
        "platen_height": 450,
        "tie_bar_spacing_h": 360,
        "tie_bar_spacing_v": 360,
        "typical_use": "Small-medium parts"
    },
    {
        "name": "180T Standard",
        "manufacturer": "Generic",
        "tonnage": 180,
        "shot_volume_max": 300,
        "screw_diameter": 40,
        "platen_width": 500,
        "platen_height": 500,
        "tie_bar_spacing_h": 410,
        "tie_bar_spacing_v": 410,
        "typical_use": "Medium parts"
    },
    {
        "name": "250T Standard",
        "manufacturer": "Generic",
        "tonnage": 250,
        "shot_volume_max": 500,
        "screw_diameter": 50,
        "platen_width": 600,
        "platen_height": 600,
        "tie_bar_spacing_h": 480,
        "tie_bar_spacing_v": 480,
        "typical_use": "Medium parts"
    },
    {
        "name": "350T Standard",
        "manufacturer": "Generic",
        "tonnage": 350,
        "shot_volume_max": 800,
        "screw_diameter": 55,
        "platen_width": 700,
        "platen_height": 700,
        "tie_bar_spacing_h": 560,
        "tie_bar_spacing_v": 560,
        "typical_use": "Medium-large parts"
    },
    {
        "name": "500T Standard",
        "manufacturer": "Generic",
        "tonnage": 500,
        "shot_volume_max": 1200,
        "screw_diameter": 65,
        "platen_width": 800,
        "platen_height": 800,
        "tie_bar_spacing_h": 650,
        "tie_bar_spacing_v": 650,
        "typical_use": "Large parts"
    },
    {
        "name": "650T Standard",
        "manufacturer": "Generic",
        "tonnage": 650,
        "shot_volume_max": 1800,
        "screw_diameter": 70,
        "platen_width": 900,
        "platen_height": 900,
        "tie_bar_spacing_h": 730,
        "tie_bar_spacing_v": 730,
        "typical_use": "Large parts"
    },
    {
        "name": "850T Standard",
        "manufacturer": "Generic",
        "tonnage": 850,
        "shot_volume_max": 2500,
        "screw_diameter": 80,
        "platen_width": 1000,
        "platen_height": 1000,
        "tie_bar_spacing_h": 820,
        "tie_bar_spacing_v": 820,
        "typical_use": "Very large parts"
    },
    {
        "name": "1000T Standard",
        "manufacturer": "Generic",
        "tonnage": 1000,
        "shot_volume_max": 3500,
        "screw_diameter": 90,
        "platen_width": 1100,
        "platen_height": 1100,
        "tie_bar_spacing_h": 900,
        "tie_bar_spacing_v": 900,
        "typical_use": "Very large parts"
    },
    {
        "name": "1300T Standard",
        "manufacturer": "Generic",
        "tonnage": 1300,
        "shot_volume_max": 5000,
        "screw_diameter": 100,
        "platen_width": 1200,
        "platen_height": 1200,
        "tie_bar_spacing_h": 980,
        "tie_bar_spacing_v": 980,
        "typical_use": "Extra large parts"
    },
]


async def seed_database(session):
    """Seed the database with initial materials and machines."""
    from app.models import Material, Machine
    from sqlalchemy import select

    # Check if already seeded
    result = await session.execute(select(Material).limit(1))
    if result.scalar():
        return  # Already seeded

    # Add materials
    for mat_data in MATERIALS_SEED:
        material = Material(**mat_data)
        session.add(material)

    # Add machines
    for mach_data in MACHINES_SEED:
        machine = Machine(**mach_data)
        session.add(machine)

    await session.commit()
