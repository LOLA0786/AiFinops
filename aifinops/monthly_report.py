from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
import json, datetime as dt

def generate_monthly_report(costs, gpu_stats, forecast):
    doc = SimpleDocTemplate("finops_monthly_report.pdf", pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("<b>AiFinOps Monthly Report</b>", styles['Title']))
    story.append(Paragraph(f"Generated: {dt.datetime.utcnow()}", styles['Normal']))
    story.append(Paragraph("<b>Cost Summary:</b>", styles['Heading2']))
    story.append(Paragraph(str(costs), styles['Code']))

    story.append(Paragraph("<b>GPU Waste Summary:</b>", styles['Heading2']))
    story.append(Paragraph(str(gpu_stats), styles['Code']))

    story.append(Paragraph("<b>Forecast:</b>", styles['Heading2']))
    story.append(Paragraph(str(forecast), styles['Code']))

    doc.build(story)
    return "finops_monthly_report.pdf"
