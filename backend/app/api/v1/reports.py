from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path

from app.database import get_db
from app.models import Analysis, Report, Material, Part
from app.schemas import ReportRequest
from app.config import settings

router = APIRouter()

@router.post("/generate")
async def generate_report(
    request: ReportRequest,
    db: AsyncSession = Depends(get_db)
):
    """Generate report for an analysis."""
    # Get analysis with related data
    analysis = await db.get(Analysis, request.analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    part = await db.get(Part, analysis.part_id)
    material = await db.get(Material, analysis.material_id)

    # Generate report content
    if request.format == "html":
        content, filename = generate_html_report(
            analysis, part, material, request.report_type
        )
        file_path = settings.REPORTS_DIR / filename
        with open(file_path, 'w') as f:
            f.write(content)
    elif request.format == "pdf":
        # For PDF, generate HTML first then convert
        html_content, _ = generate_html_report(
            analysis, part, material, request.report_type
        )
        filename = f"report_{analysis.id}_{request.report_type}.pdf"
        file_path = settings.REPORTS_DIR / filename

        try:
            from weasyprint import HTML
            HTML(string=html_content).write_pdf(file_path)
        except Exception as e:
            # Fallback to HTML if PDF generation fails
            filename = f"report_{analysis.id}_{request.report_type}.html"
            file_path = settings.REPORTS_DIR / filename
            with open(file_path, 'w') as f:
                f.write(html_content)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {request.format}")

    # Save report record
    report = Report(
        analysis_id=analysis.id,
        report_type=request.report_type,
        format=request.format,
        file_path=str(file_path)
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)

    return {
        "id": report.id,
        "file_path": str(file_path),
        "format": request.format,
        "generated_at": report.generated_at
    }

@router.get("/{report_id}/download")
async def download_report(report_id: int, db: AsyncSession = Depends(get_db)):
    """Download generated report."""
    report = await db.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    file_path = Path(report.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Report file not found")

    return FileResponse(
        path=file_path,
        filename=file_path.name,
        media_type="application/octet-stream"
    )


def generate_html_report(analysis, part, material, report_type: str) -> tuple:
    """Generate HTML report content."""

    # Determine feasibility color
    feasibility_colors = {
        "feasible": "#22c55e",
        "borderline": "#f59e0b",
        "not_recommended": "#ef4444"
    }
    status_color = feasibility_colors.get(analysis.feasibility_status, "#6b7280")

    # Format warnings
    warnings_html = ""
    if analysis.warnings:
        for w in analysis.warnings:
            msg = w.get("customer_message" if report_type == "customer" else "designer_message", "")
            severity_colors = {"low": "#3b82f6", "medium": "#f59e0b", "high": "#ef4444"}
            color = severity_colors.get(w.get("severity", "low"), "#6b7280")
            warnings_html += f'<div style="padding: 8px; margin: 4px 0; border-left: 4px solid {color}; background: #f9fafb;">{msg}</div>'

    # Format machines
    machines_html = ""
    if analysis.recommended_machines:
        for m in analysis.recommended_machines[:3]:
            machine = m.get("machine", {})
            suitability = m.get("suitability", "")
            machines_html += f'''
            <tr>
                <td>{machine.get("name", "")}</td>
                <td>{machine.get("tonnage", "")}T</td>
                <td>{suitability}</td>
            </tr>
            '''

    if report_type == "customer":
        # Customer-friendly report
        html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Mold Flow Analysis - Summary Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; color: #333; }}
                .header {{ border-bottom: 2px solid #2563eb; padding-bottom: 20px; margin-bottom: 30px; }}
                .feasibility {{ font-size: 24px; font-weight: bold; color: {status_color}; padding: 20px; background: #f9fafb; border-radius: 8px; text-align: center; margin: 20px 0; }}
                .section {{ margin: 20px 0; }}
                .section h2 {{ color: #1e40af; border-bottom: 1px solid #e5e7eb; padding-bottom: 8px; }}
                .metric {{ display: inline-block; margin: 10px 20px 10px 0; }}
                .metric-value {{ font-size: 28px; font-weight: bold; color: #1e40af; }}
                .metric-label {{ font-size: 12px; color: #6b7280; }}
                table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
                th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #e5e7eb; }}
                th {{ background: #f3f4f6; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Mold Flow Analysis Report</h1>
                <p>Part: {part.name} | Material: {material.name}</p>
            </div>

            <div class="feasibility">
                {analysis.feasibility_status.upper().replace("_", " ")}
            </div>

            <div class="section">
                <h2>Key Numbers</h2>
                <div class="metric">
                    <div class="metric-value">{analysis.clamp_tonnage_recommended:.0f}T</div>
                    <div class="metric-label">Recommended Machine</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{analysis.cycle_time:.1f}s</div>
                    <div class="metric-label">Cycle Time</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{analysis.part_weight:.1f}g</div>
                    <div class="metric-label">Part Weight</div>
                </div>
            </div>

            <div class="section">
                <h2>Considerations</h2>
                {warnings_html if warnings_html else '<p>No significant concerns identified.</p>'}
            </div>

            <div class="section">
                <h2>Suitable Machines</h2>
                <table>
                    <tr><th>Machine</th><th>Tonnage</th><th>Suitability</th></tr>
                    {machines_html}
                </table>
            </div>

            <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #e5e7eb; font-size: 11px; color: #6b7280;">
                <p>This is an early feasibility assessment, not a detailed CAE simulation. Results should be verified with full mold flow analysis before tool design.</p>
                <p>Generated by MouldFlow Analysis Tool</p>
            </div>
        </body>
        </html>
        '''
    else:
        # Designer technical report
        html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Mold Flow Analysis - Technical Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; color: #333; font-size: 12px; }}
                .header {{ border-bottom: 2px solid #2563eb; padding-bottom: 20px; margin-bottom: 30px; }}
                .section {{ margin: 20px 0; }}
                .section h2 {{ color: #1e40af; border-bottom: 1px solid #e5e7eb; padding-bottom: 8px; font-size: 16px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
                th, td {{ padding: 6px 8px; text-align: left; border: 1px solid #e5e7eb; }}
                th {{ background: #f3f4f6; }}
                .formula {{ font-family: monospace; background: #f3f4f6; padding: 8px; margin: 8px 0; border-radius: 4px; }}
                .warning {{ padding: 8px; margin: 4px 0; border-left: 4px solid #f59e0b; background: #fffbeb; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Mold Flow Analysis - Technical Report</h1>
                <p>Part: {part.name} | Material: {material.name} ({material.manufacturer} {material.grade})</p>
            </div>

            <div class="section">
                <h2>Part Geometry</h2>
                <table>
                    <tr><th>Parameter</th><th>Value</th><th>Unit</th></tr>
                    <tr><td>Volume</td><td>{part.volume:.2f}</td><td>cm³</td></tr>
                    <tr><td>Projected Area</td><td>{part.projected_area:.2f}</td><td>cm²</td></tr>
                    <tr><td>Bounding Box</td><td>{part.bbox_x:.1f} × {part.bbox_y:.1f} × {part.bbox_z:.1f}</td><td>mm</td></tr>
                    <tr><td>Wall Thickness (min/avg/max)</td><td>{part.min_thickness:.1f} / {part.avg_thickness:.1f} / {part.max_thickness:.1f}</td><td>mm</td></tr>
                </table>
            </div>

            <div class="section">
                <h2>Process Configuration</h2>
                <table>
                    <tr><th>Parameter</th><th>Value</th></tr>
                    <tr><td>Cavity Count</td><td>{analysis.cavity_count}</td></tr>
                    <tr><td>Gate Type</td><td>{analysis.gate_type}</td></tr>
                    <tr><td>Gate Diameter</td><td>{analysis.gate_diameter:.2f} mm</td></tr>
                    <tr><td>Runner Diameter</td><td>{analysis.runner_diameter:.2f} mm</td></tr>
                    <tr><td>Safety Factor</td><td>{analysis.safety_factor}</td></tr>
                </table>
            </div>

            <div class="section">
                <h2>Results</h2>
                <table>
                    <tr><th>Parameter</th><th>Value</th><th>Unit</th></tr>
                    <tr><td>Fill Time</td><td>{analysis.fill_time:.2f}</td><td>s</td></tr>
                    <tr><td>Injection Pressure</td><td>{analysis.injection_pressure:.1f}</td><td>MPa</td></tr>
                    <tr><td>Clamp Tonnage (min/rec/cons)</td><td>{analysis.clamp_tonnage_min:.0f} / {analysis.clamp_tonnage_recommended:.0f} / {analysis.clamp_tonnage_max:.0f}</td><td>T</td></tr>
                    <tr><td>Cycle Time</td><td>{analysis.cycle_time:.1f}</td><td>s</td></tr>
                    <tr><td>Cooling Time</td><td>{analysis.cooling_time:.1f}</td><td>s</td></tr>
                    <tr><td>Part Weight</td><td>{analysis.part_weight:.2f}</td><td>g</td></tr>
                    <tr><td>Shot Weight</td><td>{analysis.shot_weight:.2f}</td><td>g</td></tr>
                </table>
            </div>

            <div class="section">
                <h2>Clamp Tonnage Calculation</h2>
                <div class="formula">
                    F = A × n × P × SF<br>
                    F = {part.projected_area:.1f} × {analysis.cavity_count} × {analysis.injection_pressure:.1f} × {analysis.safety_factor}<br>
                    F = {analysis.clamp_tonnage_recommended:.1f} metric tons
                </div>
                <p style="font-size: 10px; color: #6b7280;">Reference: Rosato, Injection Molding Handbook</p>
            </div>

            <div class="section">
                <h2>Warnings & Recommendations</h2>
                {warnings_html if warnings_html else '<p>No warnings generated.</p>'}
            </div>

            <div class="section">
                <h2>Machine Recommendations</h2>
                <table>
                    <tr><th>Machine</th><th>Tonnage</th><th>Suitability</th></tr>
                    {machines_html}
                </table>
            </div>

            <div class="section">
                <h2>Material Properties</h2>
                <table>
                    <tr><th>Property</th><th>Value</th></tr>
                    <tr><td>Melt Temperature</td><td>{material.melt_temp_min}–{material.melt_temp_max} °C</td></tr>
                    <tr><td>Mold Temperature</td><td>{material.mold_temp_min}–{material.mold_temp_max} °C</td></tr>
                    <tr><td>Density</td><td>{material.density} g/cm³</td></tr>
                    <tr><td>Shrinkage</td><td>{material.shrinkage_min}–{material.shrinkage_max} %</td></tr>
                    <tr><td>Max Flow L/t Ratio</td><td>{material.max_flow_length_ratio}</td></tr>
                </table>
            </div>

            <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #e5e7eb; font-size: 10px; color: #6b7280;">
                <p><strong>Disclaimer:</strong> This is an early feasibility tool using analytical approximations, not a detailed CAE simulation. Results should be verified with full mold flow analysis before finalizing tool design.</p>
                <p>Generated by MouldFlow Analysis Tool | Feasibility Score: {analysis.feasibility_score}/100</p>
            </div>
        </body>
        </html>
        '''

    filename = f"report_{analysis.id}_{report_type}.html"
    return html, filename
