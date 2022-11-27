from os.path import join, dirname

from kivy.animation import Animation
from kivy.lang import Builder

from Views.Popups.confirm_delete.confirm_delete import ConfirmDelete
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog

from typing import TYPE_CHECKING

from kivymd.uix.list import TwoLineAvatarIconListItem
from kivymd.uix.snackbar import Snackbar

if TYPE_CHECKING:
    from Model.main_model import MainModel
    from Controller.form_view_controller import FormViewController
    from kivymd.uix.selection.selection import SelectionItem


class MultiSelectPopup(MDDialog):
    def __init__(self, title, model: 'MainModel', controller: 'FormViewController', ind, db,
                 selections=None, selected=None, signatures=False, **kwargs):
        self.buttons = [MDFlatButton(text='Select All', on_press=self.select_all,
                                     md_bg_color=(0.49, 0.545, 0.376, 1)),
                        MDFlatButton(text='Submit', on_press=self.submit_button)]
        super().__init__(**kwargs)
        self.model = model
        self.controller = controller
        self.size_hint_x = 1
        self.content_cls.delete_button = MDFlatButton(text='Delete', on_press=self.content_cls.delete_fields,
                                                      md_bg_color=(0.545, 0.431, 0.376, 1))
        self.content_cls.popup = self
        self.title = title
        self.id = ind
        self.db = db
        self.signatures = signatures
        self.selections = selections
        if self.content_cls.equipment:
            self.selected = {} if selected is None else selected
        else:
            self.selected = [] if selected is None else list(selected)
        self.content_cls.selections = self.selected
        self.content_cls.pop_selection_list(fields=self.selections)

    def select_all(self, obj):
        self.content_cls.select_all()

    def submit_button(self, obj):
        self.content_cls.submit_button()
        screen = self.screen_manager.get_screen('form_view')
        for m in screen.multi:
            if m.title == self.title and not self.content_cls.equipment:
                m.add_button_text(self.selected)


class CheckBoxRow(MDBoxLayout):
    def __init__(self, selection_list, **kwargs):
        super().__init__(**kwargs)
        self.result = 'P'
        self.selection_list = selection_list

    def on_checkbox_active(self, *args):
        self.selection_list.result = self.result
        self.selection_list.on_checkbox_active(*args)


class SegmentedControlRow(MDBoxLayout):
    def __init__(self, selection_list, **kwargs):
        super().__init__(**kwargs)
        self.result_map = {'Pass': 'P', 'Needs Maintenance': 'M', 'Fail': 'R'}
        self.result = 'P'
        self.selection_list = selection_list

    def on_active(self, segment_control, segmented_item):
        self.result = self.result_map[segmented_item.text]
        self.selection_list.result = self.result
        self.selection_list.on_checkbox_active()


class MultiSelectPopupContent(MDBoxLayout):
    def __init__(self, popup: 'MultiSelectPopup' = None, equipment=False, selections=None, field_ids=None, **kwargs):
        super().__init__(**kwargs)
        self.popup = popup
        self.fields = None
        self.equipment = equipment
        if self.equipment:
            self.field_ids = field_ids
            self.selection_colors = {"P": 'green', "M": 'yellow', "R": 'red'}
            self.selections = {} if selections is None else dict(selections)
            self.result = 'P'
            self.ids.top_content.remove_widget(self.ids.add_new)
            self.ids.top_content.remove_widget(self.ids.add_button)
            self.ids.top_content.add_widget(CheckBoxRow(selection_list=self))
            # self.ids.top_content.add_widget(SegmentedControlRow(selection_list=self))

        else:
            self.selections = [] if selections is None else list(selections)
        self.ids.selection_list.selected_mode = True
        self.pre_selected = None
        self.delete_button = None

    def on_checkbox_active(self, *args):
        self.ids.selection_list.overlay_color = self.selection_colors[self.result]

    def add_list_item(self, list_item):
        self.fields.append(list_item)

    def pop_selection_list(self, fields):
        self.fields = fields
        for num, s in enumerate(self.fields):
            i = SelectableListItem(text=str(s), popup=self.popup)
            if self.equipment:
                i.undeletable = True
                i.id = str(self.field_ids[num])
            self.ids.selection_list.add_widget(i)
        self.pre_selected = self.if_selection()
        self.show_or_hide_delete_button(self.pre_selected)
        if self.equipment:
            self.colour_selections()
        self.do_select_animation()
        if self.equipment:
            for s in self.ids.selection_list.children:
                if s.instance_item.text not in self.selections or not self.selections[s.instance_item.text]:
                    self.selections[s.instance_item.text] = 'NA'
            self.result = 'P'
            self.ids.selection_list.overlay_color = 'green'

    def if_selection(self):
        if self.equipment:
            return [s for s in self.ids.selection_list.children if s.instance_item.text in self.selections and
                    self.selections[s.instance_item.text]]
        return [s for s in self.ids.selection_list.children if s.instance_item.text in self.selections]

    def colour_selections(self):
        for s in self.ids.selection_list.children:
            if s.instance_item.text not in self.selections:
                continue
            if self.selections[s.instance_item.text] and self.selections[s.instance_item.text] != 'NA':
                for grade, colour in self.selection_colors.items():
                    self.add_colour(grade, s, colour)

    def add_colour(self, grade, list_item, colour):
        if grade in self.selections[list_item.instance_item.text]:
            list_item.overlay_color = colour

    def do_select_animation(self):
        for s in self.pre_selected:
            Animation(scale=1, d=0.2).start(s.instance_icon)
            s.selected = True

    def on_selected(self, instance_selection_list, instance_selection_item):
        if self.equipment:
            self.selections[instance_selection_item.instance_item.text] = self.result
            for x in instance_selection_list.children:
                if x.instance_item.text == instance_selection_item.instance_item.text:
                    x.overlay_color = self.ids.selection_list.overlay_color
            return
        self.selections.append(instance_selection_item.instance_item.text)
        self.show_or_hide_delete_button(self.if_selection())

    def on_unselected(self, instance_selection_list, instance_selection_item: 'SelectionItem'):
        if self.equipment:
            self.selections[instance_selection_item.instance_item.text] = 'NA'
            instance_selection_item.overlay_color = [0, 0, 0, 0.2]
            return
        if self.selections:
            self.selections.remove(instance_selection_item.instance_item.text)
        self.show_or_hide_delete_button(self.if_selection())

    def on_selected_mode(self, instance_selection_list, mode):
        if not mode:
            self.ids.selection_list.selected_mode = True

    def select_all(self):
        self.ids.selection_list.unselected_all()
        self.ids.selection_list.selected_all()

    def show_or_hide_delete_button(self, list_items):
        if [list_item for list_item in list_items if not list_item.instance_item.undeletable]:
            self.show_delete_button()
        else:
            self.hide_delete_button()

    def show_delete_button(self):
        for b in self.popup.buttons:
            if b.text == 'Delete':
                return
        self.popup.buttons.append(self.delete_button)
        self.popup.ids.button_box.add_widget(self.delete_button, index=2)

    def hide_delete_button(self):
        if self.delete_button in self.popup.buttons:
            self.popup.ids.button_box.remove_widget(self.delete_button)
            self.popup.buttons.remove(self.delete_button)

    def add_button(self):
        if self.ids.add_new.text and self.popup.db:
            self.update_fields(self.popup.model.add_form_option, self.popup)
            i = SelectableListItem(text=str(self.ids.add_new.text), popup=self.popup)
            self.ids.selection_list.add_widget(i)
            self.ids.add_new.text = ''
            return
        if not self.ids.add_new.text:
            Snackbar(text='Entry cannot be empty').open()
            return
        if not self.popup.db:
            Snackbar(text='Items cannot be added to this list from here').open()

    def delete_fields(self, obj):
        popup = ConfirmDelete(item=[list_item.instance_item.text
                                    for list_item in self.ids.selection_list.get_selected_list_items()],
                              feed=self.popup.title, button=None, form_option=True, popup=self.popup,
                              model=self.popup.model)
        popup.open()

    def update_fields(self, func, param):
        options, multi_option_fields = func(param)
        widget = next((s for s in multi_option_fields if self.popup.id == s.id), None)
        widget.selections = options

    def submit_button(self):
        self.popup.selections = self.selections
        self.popup.controller.save_fields(popup=self.popup, number='multi', equipment=self.equipment)
        self.popup.dismiss()


class SelectableListItem(TwoLineAvatarIconListItem):
    def __init__(self, text, popup: 'MultiSelectPopup', undeletable=False, **kwargs):
        super(SelectableListItem, self).__init__(**kwargs)
        self.text = text
        self.id = ''
        self.undeletable = undeletable
        self.popup = popup
        if self.popup.model.is_undeletable(title=self.popup.title, text=self.text):
            self.undeletable = True


Builder.load_file(join(dirname(__file__), "multi_select_popup_content.kv"))
Builder.load_file(join(dirname(__file__), "segmented_control.kv"))
Builder.load_file(join(dirname(__file__), "checkbox_row.kv"))