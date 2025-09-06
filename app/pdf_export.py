from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from textwrap import wrap

def export_edge_sheet_pdf(filepath: str, title: str, tldr: str, bullets: list):
    c = canvas.Canvas(filepath, pagesize=LETTER)
    width, height = LETTER
    y = height - 72
    c.setFont("Helvetica-Bold", 16); c.drawString(72, y, title); y -= 28
    c.setFont("Helvetica", 12)
    for line in wrap("TL;DR: " + tldr, 95):
        c.drawString(72, y, line); y -= 16
    y -= 8
    for b in bullets:
        for line in wrap("• " + b, 95):
            c.drawString(72, y, line); y -= 16
        y -= 8
    c.showPage(); c.save()
