from reportlab.platypus import Flowable
from reportlab.lib import colors


class InteractiveCheckBox(Flowable):
    def __init__(self, name, tooltip="", checked=False, size=12, button_style="check"):
        Flowable.__init__(self)
        self.name = name
        self.tooltip = tooltip
        self.size = size
        self.check = checked
        self.buttonStyle = button_style

    def draw(self):
        self.canv.saveState()
        form = self.canv.acroForm
        form.checkbox(checked=self.check,
                      buttonStyle=self.buttonStyle,
                      name=self.name,
                      tooltip=self.tooltip,
                      relative=True,
                      size=self.size,
                      fillColor=colors.white)
        self.canv.restoreState()
