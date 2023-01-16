from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Image
from reportlab.lib.pagesizes import letter


class Header:
    def __init__(self):
        pdfmetrics.registerFont(TTFont('BankGothicBold', 'assets/BankGothicBold.ttf'))
        self.logo_width = 1.5  # in inches
        self.paragraph_style = ParagraphStyle(name='sbs_header', fontName='BankGothicBold', fontSize=24,
                                              spaceBefore=6, spaceAfter=6, leading=18)

    def letter_head(self, canvas, doc):
        self.logo(canvas, doc)
        self.logo_text(canvas, doc)
        self.underline(canvas, doc)

        canvas.saveState()
        canvas.restoreState()

    def logo(self, canvas, doc):
        canvas.saveState()
        header = Image("assets/sbs.png", self.logo_width * inch, (self.logo_width * (69 / 158)) * inch)
        header.drawOn(canvas, 3 * cm, doc.height + doc.topMargin)
        canvas.restoreState()

    def logo_text(self, canvas, doc):
        canvas.saveState()
        text = Paragraph("SEAGRAVE BUILDING SYSTEMS LTD.", self.paragraph_style)
        text.wrapOn(canvas, aH=1.5 * inch, aW=4.5 * inch)
        text.drawOn(canvas, doc.leftMargin + 1.75 * inch, doc.height + doc.topMargin + 0.6 * cm)
        canvas.restoreState()

    def underline(self, canvas, doc):
        canvas.saveState()
        y = doc.height + doc.topMargin - (self.logo_width * (69 / 158)) - 0.2 * cm
        canvas.line(1 * cm, y, letter[0] - 1 * cm, y)
        canvas.restoreState()
