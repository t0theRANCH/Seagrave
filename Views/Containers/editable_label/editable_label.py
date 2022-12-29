from os.path import join, dirname

from kivy.lang import Builder
from kivy.properties import BooleanProperty, StringProperty

from kivymd.uix.relativelayout import MDRelativeLayout


class EditableLabel(MDRelativeLayout):
    edit = BooleanProperty(False)
    text = StringProperty('')
    hint_text = StringProperty('')

    def __init__(self, **kwargs):
        super(EditableLabel, self).__init__(**kwargs)

    def on_touch_down(self, touch):
        if not self.edit:
            return True
        if self.collide_point(*touch.pos):
            return super(EditableLabel, self).on_touch_down(touch)

    def edit_text(self, instance):
        if self.edit:
            self.edit = False
            return
        self.edit = True

    def on_edit(self, instance, value):
        if self.edit:
            self.ids.text_field.focus = True
            self.ids.text_field.select_all()
            return
        self.ids.text_field.focus = False


Builder.load_file(join(dirname(__file__), "editable_label.kv"))
