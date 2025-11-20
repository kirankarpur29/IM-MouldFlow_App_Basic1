# MouldFlow Analysis

An open-source web application for early-stage injection molding feasibility assessment. Provides quick, transparent analysis for mold designers and customers.

## Features

- **STL File Upload**: Automatic geometry analysis (volume, projected area, thickness)
- **Material Database**: 20+ materials with manufacturer-specific grades (SABIC, LG Chem, BASF, Covestro, DuPont)
- **Core Calculations**:
  - Clamp tonnage estimation
  - Fill time and injection pressure
  - Cycle time breakdown
  - Gate and runner sizing
- **Machine Recommendations**: Matches requirements to standard machine tonnages
- **Dual Views**:
  - Designer View: Full technical details with formulas
  - Customer View: Simplified summary with plain language
- **Report Generation**: PDF reports with all calculations and citations

## Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/mouldflow-analysis.git
cd mouldflow-analysis

# Start the application
docker-compose up --build

# Access the app
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

### Manual Setup

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Technology Stack

- **Frontend**: React 18, TypeScript, Three.js, Tailwind CSS
- **Backend**: Python FastAPI, SQLAlchemy, NumPy/SciPy
- **Database**: SQLite (development) / PostgreSQL (production)
- **Reports**: WeasyPrint (PDF generation)

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/parts/upload` | Upload STL file |
| `POST /api/v1/analysis/` | Run mold flow analysis |
| `GET /api/v1/materials/` | List available materials |
| `GET /api/v1/machines/` | List available machines |
| `POST /api/v1/reports/generate` | Generate PDF/HTML report |

Full API documentation available at `/docs` when running the backend.

## Engineering Formulas

### Clamp Tonnage
```
F = A × n × P × SF
```
Where:
- A = Projected area (cm²)
- n = Number of cavities
- P = Cavity pressure (MPa)
- SF = Safety factor (typically 1.15)

Reference: Rosato, "Injection Molding Handbook"

### Cycle Time
```
Cooling Time ≈ k × t²
```
Where:
- k = Material-specific coefficient
- t = Maximum wall thickness (mm)

Reference: Menges, "How to Make Injection Molds"

## Material Database

Includes generic and manufacturer-specific grades:
- ABS: Generic, SABIC Cycolac MG47, LG HI121H
- PP: Generic, SABIC 500P, LyondellBasell Moplen HP500N
- PC: Generic, Covestro Makrolon 2405, SABIC Lexan 141R
- PA: Generic, BASF Ultramid B3S, DuPont Zytel 101L
- POM: Generic, DuPont Delrin 500P
- And more...

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/v1/          # API endpoints
│   │   ├── calculations/    # Engineering formulas
│   │   ├── models/          # Database models
│   │   ├── services/        # Business logic
│   │   └── main.py          # FastAPI app
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   └── api/             # API client
│   └── package.json
├── docker-compose.yml
└── README.md
```

## Disclaimer

This is an **early-stage feasibility tool** using analytical approximations, not a detailed CAE simulation. Results provide quick decision support but should be verified with full mold flow analysis (Moldex3D, Moldflow, etc.) before finalizing tool design.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

Areas for contribution:
- Additional materials with validated data
- Improved calculation algorithms
- UI/UX enhancements
- Documentation and tutorials
