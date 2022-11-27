from os.path import join, dirname

from kivy.lang import Builder

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Model.main_model import MainModel
    from Views.Screens.form_view.form_view import FormView


class RiskPopup(MDDialog):
    def __init__(self, **kwargs):
        self.buttons = [MDFlatButton(text='Cancel', on_press=self.dismiss),
                        MDFlatButton(text='Done', on_press=self.submit)]
        super().__init__(**kwargs)
        self.content_cls.popup = self

    def submit(self, obj):
        self.content_cls.submit_button()


class RiskPopupContent(MDBoxLayout):
    def __init__(self, title: str, model: 'MainModel', view: 'FormView', ind: str, signatures=None, **kwargs):
        super().__init__(**kwargs)
        self.id = ind
        self.title = title
        self.model = model
        self.view = view
        self.signatures = signatures
        self.popup = None
        if self.id in self.model.form_view_fields['risk']:
            self.risk = self.model.form_view_fields['risk'][self.id]['risk']
            self.priority = self.model.form_view_fields['risk'][self.id]['priority']
        else:
            self.risk = '1'
            self.priority = 'A'
        for s in self.ids:
            if s in self.risk or s in self.priority:
                self.ids[s].active = True

    def submit_button(self):
        if not self.risk:
            self.risk = '1'
        if not self.priority:
            self.priority = 'A'
        self.model.form_view_fields['risk'].update({self.id: {"risk": self.risk, "priority": self.priority}})
        self.view.get_tree()
        for r in self.model.risk:
            if r.id in self.model.form_view_fields['risk']:
                r.select()
                r.add_button_text(f"{self.risk}{self.priority}")
        self.popup.dismiss()


Builder.load_file(join(dirname(__file__), "risk_popup.kv"))
