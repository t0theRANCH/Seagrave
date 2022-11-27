from os.path import join, dirname

from kivy.lang import Builder

from kivymd.toast import toast
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import IconLeftWidget, ThreeLineIconListItem, OneLineIconListItem

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Controller.site_view_controller import SiteViewController


class FormContent(MDBoxLayout):
    def __init__(self, new_form_data, incomplete_form_data, complete_form_data,
                 controller: 'SiteViewController', **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self.new_form_data = new_form_data
        self.incomplete_form_data = incomplete_form_data
        self.complete_form_data = complete_form_data
        self.popup = None

    def list_new_forms(self):
        items = [OneLineIconListItem(IconLeftWidget(icon='note-plus'), text=f, on_release=self.start_new_form)
                 for f in self.new_form_data]
        self.popup = MDDialog(title='Fill Out New Form', items=items, type='simple')
        self.popup.size_hint_x = 1
        self.popup.open()

    def list_incomplete_forms(self):
        if items := [ThreeLineIconListItem(IconLeftWidget(icon='note-edit'),
                                           text=v['name'],
                                           secondary_text=v['date'],
                                           tertiary_text=v['separator'],
                                           id=k, on_release=self.finish_incomplete_form)
                     for k, v in self.incomplete_form_data.items()]:
            self.popup = MDDialog(title='Finish Incomplete Form', items=items, type='simple')
            self.popup.size_hint_x = 1
            self.popup.open()
            return
        toast(text='There are no incomplete forms for this site')

    def list_complete_forms(self):
        if items := [ThreeLineIconListItem(IconLeftWidget(icon='note-check'),
                                           text=v['name'],
                                           secondary_text=v['date'],
                                           tertiary_text=v['separator'],
                                           id=v['file_name'],
                                           on_release=self.view_form)
                     for k, v in self.complete_form_data.items()]:
            self.popup = MDDialog(title='View Completed Form', items=items, type='simple')
            self.popup.size_hint_x = 1
            self.popup.open()
            return
        toast(text='There are no completed forms for this site')

    def start_new_form(self, instance_item: IconLeftWidget):
        form_id = str(instance_item.text).lower().replace(' ', '_')
        self.controller.switch_to_form_view(form_id=form_id)
        self.popup.dismiss()

    def finish_incomplete_form(self, instance_item: IconLeftWidget):
        self.controller.switch_to_form_view(form_id=instance_item.id)
        self.popup.dismiss()

    def view_form(self, instance_item: IconLeftWidget):
        self.controller.model.download_form(button_id=instance_item.id)
        self.popup.dismiss()


Builder.load_file(join(dirname(__file__), "form_content.kv"))
