from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle

def create_pdf(filename):
    # Set up the canvas with a specific page size
    c = canvas.Canvas(filename, pagesize=A4)
    c.setTitle("Well Architected Review")
    # Draw a string on the PDF at coordinates (x, y)
    c.drawString(500, 780, "Hello")
    c.drawString(50, 50, "This report was generated using Python and ReportLab.")
    data = [
        ["Product", "Units Sold", "Revenue"],
        ["Product A", "100", "$1,000"],
        ["Product B", "150", "$1,500"],
        ["Product C", "200", "$2,000"]
    ]

    # Define the table and its style
    table = Table(data)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    table.setStyle(style)

    # Wrap the table and draw it on the canvas
    table.wrapOn(c, 400, 400)
    table.drawOn(c, 100, 600)
    # Save the canvas to create the PDF file
    c.save()

if __name__ == "__main__":
    create_pdf("simple_report.pdf")