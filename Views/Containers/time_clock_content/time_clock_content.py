from datetime import datetime
from os.path import join, dirname

from kivy.lang import Builder

from kivymd.uix.boxlayout import MDBoxLayout

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Controller.site_view_controller import SiteViewController


class TimeClockContent(MDBoxLayout):
    def __init__(self, time_clock_data: dict, controller: 'SiteViewController', **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self.time_clock_data = time_clock_data
        self.current_day = self.get_current_day()
        self.status = self.get_status()
        self.total_hours = self.get_total_hours()
        self.set_punch_button_text()
        self.set_total_hours_text()

    @staticmethod
    def get_current_day():
        return datetime.now().strftime('%A')

    def get_status(self):
        if self.current_day in self.time_clock_data and self.time_clock_data[self.current_day]['in']:
            return 'out'
        return 'in'

    def get_total_hours(self):
        total_hours = 0
        for data in dict(self.time_clock_data).values():
            if not data['clock_out']:
                continue
            punch_in = datetime.strptime(data['clock_in'], '%Y-%m-%d %H:%M:%S')
            punch_out = datetime.strptime(data['clock_out'], '%Y-%m-%d %H:%M:%S')
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
        self.controller.punch_clock(current_datetime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    current_day=self.get_current_day(),
                                    action=self.status
                                    )
        self.set_status()
        self.set_punch_button_text()


Builder.load_file(join(dirname(__file__), "time_clock_content.kv"))
