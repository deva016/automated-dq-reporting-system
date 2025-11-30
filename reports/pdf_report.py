from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
import pandas as pd

def generate_pdf(profile, checks):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 750, "Data Quality Report")

    c.setFont("Helvetica", 12)
    c.drawString(50, 720, f"Total Rows: {profile['summary'].get('n_rows', '-')}")
    c.drawString(50, 700, f"Total Columns: {profile['summary'].get('n_cols','-')}")
    c.drawString(50, 680, f"Missing Values: {profile['summary'].get('missing_values', '-')}")

    c.drawString(50, 650, f"DQ Score: {checks.get('dq_score', 0):.2f}")

    c.drawString(50, 620, "Violations:")
    y = 600
    violations = checks.get("violations")
    if isinstance(violations, pd.DataFrame) and not violations.empty:
        for idx, row in violations.head(10).iterrows():
            line = f"{row.get('column','-')} - {row.get('type','-')} - {row.get('details','-')}"
            c.drawString(70, y, line[:100])
            y -= 18
            if y < 50:
                c.showPage()
                y = 750
    else:
        c.drawString(70, 600, "No violations found.")

    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer
