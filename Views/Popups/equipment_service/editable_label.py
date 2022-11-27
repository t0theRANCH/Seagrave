import contextlib
from os.path import join, dirname
from string import capwords

from kivy.lang import Builder
from kivy.properties import BooleanProperty, StringProperty

from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.textfield import MDTextField


class EditableLabel(MDFloatLayout):
    edit = BooleanProperty(False)
    text_input = StringProperty(None, allownone=True)
    blank_text = StringProperty("<blank>")
    input_type = StringProperty('text')
    cap_words = BooleanProperty(False)

    field_text = StringProperty('')
    label_text = StringProperty('')
    font_name = StringProperty('')

    def __init__(self, **kwargs):
        super(EditableLabel, self).__init__(**kwargs)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and not self.edit:
            self.edit = True
        return super(EditableLabel, self).on_touch_down(touch)

    def on_edit(self, instance, value):
        if not value:
            if self.text_input:
                self.remove_widget(self.text_input)
            return
        self.text_input = t = MDTextField(text=self.text, size_hint=(None, None), font_size=self.font_size,
                                          pos=self.pos, size=self.size, multiline=False, input_type=self.input_type)
        self.text_input.halign = 'center'
        self.text_input.valign = 'middle'
        self.text_input.padding = [0, (self.text_input.height / 2.0 - (self.text_input.line_height / 2)), 0, 0]
        self.bind(pos=t.setter('pos'), size=t.setter('size'))
        self.add_widget(self.text_input)
        t.bind(on_text_validate=self.on_text_validate, focus=self.on_text_focus)

    def on_text_validate(self, instance):
        self.field_text = instance.text
        self.edit = False

    def on_text_focus(self, instance, focus):
        self.font_name = instance.font_name
        if self.input_type == 'number' and instance.text != '0':
            with contextlib.suppress(Exception):
                instance.text.lstrip('0')
        if self.cap_words:
            instance.text = capwords(instance.text)
        if instance.text == ' ':
            instance.text = ''
        if focus is False:
            self.field_text = self.blank_text if instance.text == '' else instance.text
            self.edit = False


Builder.load_file(join(dirname(__file__), "editable_label.kv"))
