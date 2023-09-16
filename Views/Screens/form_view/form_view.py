from os.path import join, dirname

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivymd.uix.dialog import MDDialog
from kivymd.uix.taptargetview import MDTapTargetView

from Forms.form_fields.form_widgets import SingleOption, SingleOptionDatePicker, SignatureOption, RiskButton
from Views.Popups.error_popup.error_popup import ErrorPopup
from Views.Popups.signature_popup.signature_popup import SignaturePopup, SignaturePopupContent
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.button.button import MDFloatingRootButton

from typing import TYPE_CHECKING, Union
if TYPE_CHECKING:
    from Controller.form_view_controller import FormViewController
    from Model.main_model import MainModel


class FormView(MDScreen):
    controller: 'FormViewController' = ObjectProperty()
    model: 'MainModel' = ObjectProperty()
    previous_screen = StringProperty(allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = 'forms'
        self.dialog = None
        self.speed_dial_with_save_button = {
            "Back": ["arrow-left-circle", "on_release", self.controller.remove_widgets],
            "Save": ["content-save", "on_release", self.controller.save_form],
            "Submit": ["send-check", "on_release", self.controller.submit_form]
        }
        self.speed_dial_without_save_button = {
            "Back": ["arrow-left-circle", "on_release", self.controller.remove_widgets],
            "Submit": ["send-check", "on_release", self.controller.submit_form]
        }
        self.add_save_button()

    def tap_target(self):
        speed_dial = None
        for child in self.ids.speed_dial.children:
            if isinstance(child, MDFloatingRootButton):
                speed_dial = child
        tap_target_view = MDTapTargetView(
            widget=speed_dial,
            title_text="All Finished?",
            description_text="Click Here to Submit the Form",
            widget_position="right_bottom",
            cancelable=True
        )
        tap_target_view.start()
        self.model.update_tutorial_settings('form_view_complete', False)

    def set_button_position(self, *args):
        self.controller.main_controller.view.update_fab_pos(self.ids.speed_dial)

    def on_pre_enter(self):
        Clock.schedule_once(self.set_button_position(), 0.3)

    def on_enter(self, *args):
        if self.model.settings['Tutorials'] and self.model.settings['Tutorial']['form_view_welcome']:
            self.show_tutorial()

    def on_leave(self, *args):
        screen_manager = self.controller.main_controller.screen_manager
        next_screen = screen_manager.get_screen(screen_manager.current)
        next_screen.previous_screen = self.name

    def show_tutorial(self):
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
        self.dialog = MDDialog(title="Tutorial", text="Here you can fill out the form. Select an option to get started")
        self.dialog.open()
        self.model.update_tutorial_settings('form_view_welcome', False)

    def add_save_button(self):
        self.ids.speed_dial.data = self.speed_dial_with_save_button

    def remove_save_button(self):
        self.ids.speed_dial.data = self.speed_dial_without_save_button

    def get_tree(self):
        tree = list(self.walk())
        self.model.single = [x for x in tree if all(y in str(type(x)) for y in ['Option', 'Single'])]
        self.model.multi = [x for x in tree if all(y in str(type(x)) for y in ['Option', 'Multi'])]
        self.model.checkbox = [x for x in tree if all(y in str(type(x)) for y in ['Option', 'Check'])]
        self.model.signature = [x for x in tree if all(y in str(type(x)) for y in ['Option', 'Signature'])]
        self.model.labels = [x for x in tree if 'MDLabel' in str(type(x))]
        self.model.risk = [x for x in tree if 'Risk' in str(type(x))]

    def add_repair_widgets(self, key: str, value: str):
        z = [MDLabel(text=f"Attention Required to {key}"),
             SingleOption(ind=f"work_required_{value}", title='Work Required', pre_select=[], controller=self.controller,
                          model=self.model),
             SingleOption(ind=f"assigned_to_{value}", title='Assigned To', pre_select=[], controller=self.controller,
                          model=self.model),
             SingleOptionDatePicker(ind=f"completion_{value}", model=self.model, title='Completion Date')]
        for x in z:
            self.ids.formview.add_widget(x)
            if isinstance(x, MDLabel):
                continue
            if x.ind not in self.model.form_view_fields:
                self.model.form_view_fields[x.ind] = ''
                continue
            if self.model.form_view_fields[x.ind]:
                x.select()
                x.add_button_text(self.model.form_view_fields[x.ind])

    def delete_old_repair_widgets(self, key: str, value: str):
        widgets_to_delete = [x for x in self.model.labels if key in x.text]
        widgets_to_delete.extend([x for x in self.model.single if f"_{value}" in x.id])
        for widget in widgets_to_delete:
            self.ids.formview.remove_widget(widget)

    def add_repairman_signature(self):
        repairman_signature = SignatureOption(ind="repairman_signature", person="repairman", sign_type='Sign',
                                              model=self.model, controller=self.controller)
        if 'signatures' in self.model.form_view_fields and 'Repairman' in self.model.form_view_fields['signatures']:
            repairman_signature.select()
        self.ids.formview.add_widget(repairman_signature)

    def add_worker_signatures(self, form_entry: str, signature: str, signature_type: str):
        for s in self.model.today['forms'][form_entry]['workers']:
            sig_option = SignatureOption(ind=s, person=s, sign_type=signature_type.capitalize(), model=self.model,
                                         controller=self.controller)
            if s in self.model.today['forms'][form_entry][signature]:
                sig_option.select()
            self.ids.formview.add_widget(sig_option)

    def add_risk_plan_widgets(self, name: str, num: int, button_text: str):
        button_one = RiskButton(ind=name, view=self, title=button_text,
                                model=self.model, controller=self.controller)
        button_two = SingleOption(ind=f"Plan - {name}", selection=self.model.form_view_fields['plan'][name],
                                  title=f"Plans to Eliminate/Control - {name}", plan_field=True,
                                  controller=self.controller, model=self.model)

        if self.model.form_view_fields['risk'][name]['risk']:
            self.select_risk_plan_button(button_one, f"{self.model.form_view_fields['risk'][name]['risk']}\
                                                      {self.model.form_view_fields['risk'][name]['priority']}")
        if self.model.form_view_fields['plan'][name]:
            self.select_risk_plan_button(button_two, self.model.form_view_fields['plan'][name])
        self.ids.formview.add_widget(button_one, index=(-7 - (num * 2)))
        self.ids.formview.add_widget(button_two, index=(-8 - (num * 2)))

    @staticmethod
    def select_risk_plan_button(button: Union['RiskButton', 'SingleOption'], button_text: str):
        button.select()
        button.add_button_text(button_text)

    def remove_signature_widgets(self):
        for s in self.model.signature:
            self.ids.formview.remove_widget(s)

    def add_signature_widgets(self, selection: str):
        if 'signatures' in self.model.form_view_fields:
            self.create_and_add_signature_widget(selection, 'Sign', 'signatures')
        if 'initials' in self.model.form_view_fields:
            self.create_and_add_signature_widget(selection, 'Initial', 'initials')

    def create_and_add_signature_widget(self, selection: str, sign_type: str, sign_key: str):
        sig = SignatureOption(ind=selection, person=selection, sign_type=sign_type, model=self.model,
                              controller=self.controller)
        if selection in self.model.form_view_fields[sign_key]:
            sig.select()
        self.ids.formview.add_widget(sig)

    def open_error_popup(self):
        popup = ErrorPopup(empty_fields=self.controller.pops)
        popup.open()
        self.controller.pops = []

    def open_final_signature_popup(self):
        signature_popup = SignaturePopup(content_cls=SignaturePopupContent(), type='custom',
                                         controller=self.controller, model=self.model)
        signature_popup.open()


Builder.load_file(join(dirname(__file__), "formview.kv"))
