from os.path import join, dirname

from kivy.lang import Builder

from kivymd.uix.boxlayout import MDBoxLayout

from Views.Popups.multi_select_popup.multi_select_popup import MultiSelectPopup, MultiSelectPopupContent

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Controller.site_view_controller import SiteViewController


class TimeClockContent(MDBoxLayout):
    def __init__(self, time_clock_data: dict, controller: 'SiteViewController', **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self.time_clock_data = time_clock_data
        self.current_day = self.controller.get_current_day()
        self.status = self.get_status()
        self.total_hours = self.get_total_hours()
        self.set_punch_button_text()
        self.set_total_hours_text()

    def scrim_on(self, message='', function=None):
        self.controller.main_controller.view.scrim_on(message=message)
        if function:
            self.controller.main_controller.view.async_task(function)

    def get_status(self):
        if self.current_day in self.time_clock_data and self.time_clock_data[self.current_day]['clock_in']:
            return 'out'
        return 'in'

    def get_total_hours(self):
        total_hours = 0
        for day, data in dict(self.time_clock_data).items():
            if not data['clock_out'] and self.current_day != day:
                continue
            punch_in = self.controller.format_date(data['clock_in'])
            if data['clock_out']:
                punch_out_time = data['clock_out']
            else:
                punch_out_time = self.controller.get_current_datetime()
            punch_out = self.controller.format_date(punch_out_time)
            hours = punch_out - punch_in
            total_hours += (hours.seconds // 3600)
        return total_hours

    def set_punch_button_text(self):
        self.ids.punch_button.text = f"Punch {self.status}"

    def set_total_hours_text(self):
        self.ids.total_hours.text = f"{self.total_hours} hours worked this week"

    def set_status(self):
        self.status = 'out' if self.status == 'in' else 'in'

    def punch_clock(self):
        self.scrim_on(message=f"Punching {self.status}", function=self.punch_clock_request)

    def punch_clock_request(self):
        self.controller.punch_clock(current_datetime=self.controller.get_current_datetime(),
                                    current_day=self.controller.get_current_day(),
                                    action=self.status
                                    )
        self.set_status()
        self.set_punch_button_text()

    def punch_in_other(self):
        dialog = MultiSelectPopup(title='Punch In Other', model=self.controller.model, controller=self.controller,
                                  db=None, ind=None, selections=self.controller.is_punched_out(),
                                  type='custom', content_cls=MultiSelectPopupContent(equipment=False, punch_clock=True,
                                                                                     field_ids=None))
        dialog.open()

    def punch_out_other(self):
        dialog = MultiSelectPopup(title='Punch Out Other', model=self.controller.model, controller=self.controller,
                                  db=None, ind=None, selections=self.controller.is_punched_in(),
                                  type='custom', content_cls=MultiSelectPopupContent(equipment=False, punch_clock=True,
                                                                                     field_ids=None))
        dialog.open()


Builder.load_file(join(dirname(__file__), "time_clock_content.kv"))
