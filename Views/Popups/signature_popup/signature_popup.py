from os.path import join, dirname

from kivy.graphics import Color, Ellipse, Line
from kivy.lang import Builder
from kivy.uix.stencilview import StencilView

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Model.main_model import MainModel
    from Controller.form_view_controller import FormViewController


class SignaturePopup(MDDialog):
    def __init__(self, model: 'MainModel', controller: 'FormViewController', sign_type='sign', signature=None, **kwargs):
        self.buttons = [MDFlatButton(text='Cancel', on_press=self.dismiss),
                        MDFlatButton(text='Done', on_press=self.save_screenshot)]
        self.auto_dismiss = False
        super(SignaturePopup, self).__init__(**kwargs)
        self.content_cls.popup = self
        self.model = model
        self.controller = controller
        self.sign_type = sign_type
        self.signature = signature
        self.filled = False
        if self.signature:
            self.content_cls.ids.signature.text = f"{self.sign_type} Below\n{self.signature}"
            self.content_cls.ids.sign.signature_field = self.signature

    def save_screenshot(self, obj):
        self.content_cls.ids.sign.save_screenshot()


class SignaturePopupContent(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.popup = None


class SignatureField(StencilView):
    def __init__(self, **kwargs):
        super(SignatureField, self).__init__(**kwargs)
        self.signature_field = None

    def on_touch_down(self, touch):
        with self.canvas:
            Color(0, 0, 0, 1)
            d = 5
            Ellipse(pos=(touch.x - d / 2, touch.y - d / 2), size=(d, d))
            touch.ud['line'] = Line(points=(touch.x, touch.y))

    def on_touch_move(self, touch):
        if 'line' in touch.ud:
            touch.ud['line'].points += [touch.x, touch.y]

    def save_screenshot(self):
        root = self.parent.parent.parent.parent
        full_path_prefix = f"database/{root.controller.form}_{root.model.form_view_fields[root.controller.separator]}"
        file_prefix = f"{root.controller.form}_{root.model.form_view_fields[root.controller.separator]}"
        if not self.signature_field:
            self.export_to_png(f"{full_path_prefix}_screenshot.png")
            root.controller.fill_form(f"{file_prefix}_screenshot.png")
        else:
            self.export_to_png(f"{full_path_prefix}_{self.signature_field}_{root.sign_type}.png")
            root.filled = True
            root.controller.fill_signatures(signature=f"{file_prefix}_{self.signature_field}_{root.sign_type}.png",
                                   name=self.signature_field, signature_field=True)
        root.dismiss()


Builder.load_file(join(dirname(__file__), "signature_popup.kv"))
