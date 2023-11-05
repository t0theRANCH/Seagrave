from abc import ABC, abstractmethod
from datetime import date, datetime
from os import remove
from os.path import join

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, TableStyle, Table, Spacer, Image

from Forms.interactivecheckbox import InteractiveCheckBox
from Forms.header import Header


class Form(ABC):
    name = ''
    signature_path = ''
    forms_path = ''
    company = 'Seagrave Building Systems'
    separator: str
    fields = {}
    colours = {'red': colors.red, 'green': colors.green, 'blue': colors.blue, 'black': colors.black, 'grey': colors.grey}

    def __init__(self):
        self.width = None
        self.pdf = None
        self.file_name = None
        self.today = str(date.today())
        self.date = datetime.now()
        self.date_time_string = self.date.strftime('%y_%m%d_%h%m')
        self.date_time = self.date.strftime('%y-%m-%d %h:%m')
        self.title_style = ParagraphStyle(name='title_style', fontName='BankGothicBold', fontSize=18,
                                          alignment=TA_CENTER)
        self.heading_style = ParagraphStyle(name='heading_style', fontName='BankGothicBold', fontSize=16,
                                            alignment=TA_LEFT)
        self.style_sheet = getSampleStyleSheet()
        self.letter_head = Header()
        self.flowables = []

    def header(self, canvas, doc):
        self.letter_head.letter_head(canvas, doc)
        canvas.saveState()
        canvas.restoreState()

    def make_file(self):
        self.file_name = f"{self.name.lower().replace(' ', '_').replace('/', '_')}_{self.fields.get('location', '')}_" \
                         f"{self.date_time.replace(' ', '-').replace(':', '_')}_{self.separator}"
        self.pdf = SimpleDocTemplate(join(self.forms_path, f"{self.file_name}.pdf"), pagesize=letter)
        self.width = letter[0] - self.pdf.leftMargin * 2

    def title(self, text):
        self.flowables.append(Spacer(1, 18))
        title = Paragraph(text, self.title_style)
        self.flowables.append(title)
        self.flowables.append(Spacer(1, 18))

    def heading(self, text):
        heading = Paragraph(text, self.heading_style)
        self.flowables.append(heading)
        self.flowables.append(Spacer(1, 12))

    def table(self, data, grid_format='grid', cols=None, spacer=True, style=None):
        inner_lines = {'grid': ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                       'grid_no_underline': ('LINEBEFORE', (1, 0), (1, 1), 1, colors.black),
                       'box': ('BOX', (0, 0), (-1, -1), 0.25, colors.black)}
        cols = self.get_col_widths(cols, data)
        table = Table(self.word_wrap_table(data), hAlign='LEFT', colWidths=cols)
        if style is None:
            style = [('BOX', (0, 0), (-1, -1), 0.25, colors.black), inner_lines[grid_format], ]
        if style is not False:
            table.setStyle(TableStyle(style))
        self.flowables.append(table)
        self.spacer(spacer)

    def get_col_widths(self, cols, data):
        if cols is None:
            cols = self.width / len(data[0])
        if cols == 'yes/no':
            cols = [self.width * (2 / 3), self.width / 12, self.width / 12, self.width / 12, self.width / 12]
        return cols

    def spacer(self, spacer):
        if spacer:
            self.flowables.append(Spacer(1, 12))

    @staticmethod
    def yes_no(field, check=False):
        if field:
            check = True
        return [InteractiveCheckBox(name='Yes', checked=check, tooltip="Yes"),
                InteractiveCheckBox(name='No', checked=not check, tooltip="No")]

    def paragraph(self, text, style=None):
        if style is None:
            style = self.style_sheet['Normal']
        self.flowables.append(Paragraph(text, style))

    @staticmethod
    def image(path, width, height):
        return Image(path, width, height)

    def colour(self, colour):
        return self.colours[colour]

    @staticmethod
    def inch(value):
        return value * inch

    def build(self):
        self.pdf.build(self.flowables, onFirstPage=self.header, onLaterPages=self.header)

    def signature(self, signature, title):
        if signature:
            signature = Image(signature, 2 * inch, 0.5 * inch)
        width = letter[0] - self.pdf.leftMargin * 2
        content = Table([['Signed: ', signature, 'Title: ', title]], hAlign='LEFT', rowHeights=0.4 * inch,
                        colWidths=[width / 4, width / 3, width / 12, width / 3])
        content.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 1, colors.black),
                                     ('BACKGROUND', (0, 0), (0, 1), colors.lightgrey),
                                     ('BACKGROUND', (2, 0), (2, 1), colors.lightgrey),
                                     ("VALIGN", (0, 0), (-1, -1), 'MIDDLE')]))
        self.flowables.append(content)

    @staticmethod
    def chunks(list_to_split, n):
        n = max(1, n)
        return [list_to_split[i:i + n] for i in range(0, len(list_to_split), n)]

    @staticmethod
    def level_lists(list_to_level_1, list_to_level_2):
        list_to_level_1 = list(list_to_level_1)
        list_to_level_2 = list(list_to_level_2)
        if difference := abs(len(list_to_level_1) - len(list_to_level_2)):
            min(list_to_level_1, list_to_level_2, key=len).extend([''] * difference)
        return list_to_level_1, list_to_level_2

    def word_wrap_table(self, data):
        return [[self.word_wrap_item(cell) for cell in row] for row in data]

    def word_wrap_item(self, item, italicize=False):
        style = self.style_sheet['Normal']
        style.allowOrphans = 1
        if italicize:
            item = f"<i>{item}</i>"
        return Paragraph(item, style) if isinstance(item, str) else item

    def italicize(self, item):
        style = self.style_sheet['Normal']
        return Paragraph(f"<i>{item}</i>", style)

    def remove_file(self):
        #remove(join(self.forms_path, f"{self.file_name}.pdf"))
        remove(self.signature_path)
        for signature in self.fields.get('signatures', ''):
            remove(join(self.forms_path, f"{self.fields['signatures'].get(signature, '')}"))

    @abstractmethod
    def print(self):
        pass
