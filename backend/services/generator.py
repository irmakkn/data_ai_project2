from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import ListFlowable, ListItem
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Preformatted
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Spacer
import base64
import io
from datetime import datetime


def generate_pdf_report(
    filepath,
    df,
    sector_result,
    analysis_result,
    chart_base64
):

    doc = SimpleDocTemplate(filepath, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    normal = styles["Normal"]
    heading = styles["Heading1"]

    # Title
    elements.append(Paragraph("AI Data Analysis Report", heading))
    elements.append(Spacer(1, 12))

    # Date
    elements.append(Paragraph(f"Generated at: {datetime.now()}", normal))
    elements.append(Spacer(1, 12))

    # Dataset Summary
    elements.append(Paragraph("Dataset Summary", styles["Heading2"]))
    elements.append(Spacer(1, 6))

    elements.append(Paragraph(f"Rows: {len(df)}", normal))
    elements.append(Paragraph(f"Columns: {list(df.columns)}", normal))
    elements.append(Spacer(1, 12))

    # Sector
    elements.append(Paragraph("Sector Analysis", styles["Heading2"]))
    elements.append(Spacer(1, 6))

    elements.append(Paragraph(f"Sector: {sector_result.get('sector')}", normal))
    elements.append(Paragraph(f"Confidence: {sector_result.get('confidence')}", normal))
    elements.append(Paragraph(f"Reasoning: {sector_result.get('reasoning')}", normal))
    elements.append(Spacer(1, 12))

    # Questions
    elements.append(Paragraph("Business Questions", styles["Heading2"]))
    elements.append(Spacer(1, 6))

    questions = analysis_result.get("questions", [])
    question_list = [ListItem(Paragraph(q, normal)) for q in questions]
    elements.append(ListFlowable(question_list, bulletType='bullet'))
    elements.append(Spacer(1, 12))

    # Cleaning steps
    elements.append(Paragraph("Cleaning Steps", styles["Heading2"]))
    elements.append(Spacer(1, 6))

    cleaning_steps = analysis_result.get("cleaning_steps", [])
    cleaning_list = [ListItem(Paragraph(step, normal)) for step in cleaning_steps]
    elements.append(ListFlowable(cleaning_list, bulletType='bullet'))
    elements.append(Spacer(1, 12))

    # Chart
    if chart_base64:
        elements.append(Paragraph("Visualization", styles["Heading2"]))
        elements.append(Spacer(1, 6))

        img_data = base64.b64decode(chart_base64)
        img_buffer = io.BytesIO(img_data)
        img = Image(img_buffer, width=5 * inch, height=3 * inch)
        elements.append(img)

    doc.build(elements)
