from os.path import join, dirname

from kivy.lang import Builder
from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.behaviors import FocusBehavior
from kivymd.uix.pickers import MDDatePicker

from kivymd.uix.relativelayout import MDRelativeLayout


class EditableLabel(MDRelativeLayout):
    edit = BooleanProperty(False)
    text = StringProperty('')
    hint_text = StringProperty('')

    def __init__(self, **kwargs):
        super(EditableLabel, self).__init__(**kwargs)

    def on_touch_down(self, touch):
        local = self.to_local(*touch.pos)
        if self.ids.icon.collide_point(local[0], local[1]):
            self.edit = not self.edit
            FocusBehavior.ignored_touch.append(touch)
            return True
        if self.collide_point(*touch.pos):
            if self.edit:
                self.edit = False
                FocusBehavior.ignored_touch.append(touch)
            return True

    def on_edit(self, instance, value):
        if self.edit:
            self.ids.text_field.focus = True
            self.ids.text_field.select_all()
            return
        self.ids.text_field.focus = False


class DateLabel(EditableLabel):
    def __init__(self, **kwargs):
        super(DateLabel, self).__init__(**kwargs)

    def on_edit(self, instance, value):
        pass

    def on_touch_down(self, touch):
        local = self.to_local(*touch.pos)
        if self.ids.icon.collide_point(local[0], local[1]):
            self.open_date_picker()
            FocusBehavior.ignored_touch.append(touch)
            return True
        if self.collide_point(*touch.pos):
            if self.edit:
                self.edit = False
                FocusBehavior.ignored_touch.append(touch)
            return True

    def open_date_picker(self):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_save)
        date_dialog.open()

    def on_save(self, instance, value, date_range):
        self.text = value.strftime("%d/%m/%Y")


Builder.load_file(join(dirname(__file__), "editable_label.kv"))
