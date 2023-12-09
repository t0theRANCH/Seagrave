from Forms.form import Form
from datetime import datetime, timedelta


class TimeCard(Form):
    name = 'Weekly Time Card'
    signature_path = ''
    client_signature_path = ''
    separator = ''

    def __init__(self):
        super().__init__()
        self.employees = []
        self.date = None

    def get_employees(self):
        for field in self.fields:
            n = field.split('_')
            if len(n) > 2 and n[-1] != 'location':
                self.employees.append(n[-1])

        self.employees = list(set(self.employees))

    def get_employee_data(self, employee):
        travel = self.fields[f'travel_time_{employee}']
        food_allowance = self.fields[f'food_allowance_{employee}']
        vacation = self.fields[f'vacation_pay_{employee}']
        hours = self.fields[f'{employee}_hours']
        return {'travel_time': travel, 'food_allowance': food_allowance, 'vacation_pay': vacation, 'hours': hours}

    def get_date(self):
        employee_hours = self.fields[f'{self.employees[0]}_hours']
        for time_card in employee_hours.values():
            clock_in = datetime.strptime(time_card[0], '%Y-%m-%d %H:%M:%S').date()
            weekday_num = clock_in.weekday()
            if weekday_num == 6:
                sunday = clock_in
            else:
                sunday = clock_in - timedelta(days=weekday_num)
            self.date = sunday.strftime('%B %d, %Y')
            break
        formatted_date = self.date.replace(' ', '_').replace(',', '').replace(',', '_')
        self.file_name = f'{formatted_date}_Weekly_Time_Card'

    def make_file(self, file_name=None):
        self.get_employees()
        self.get_date()
        super().make_file(file_name=self.file_name)

    def print(self):
        for employee in self.employees:
            self.print_employee(employee)
            self.new_page()
        self.build()

    def print_employee(self, employee):
        data = self.get_employee_data(employee)
        self.title(f'{employee} Weekly Time Card')
        self.heading(f'For the week starting: {self.date}')
        self.other_table(employee)
        self.hours_table(data['hours'], employee)
        
    def other_table(self, employee):
        fields = ['travel_time', 'food_allowance', 'vacation_pay']
        for field in fields:
            if not self.fields[f'{field}_{employee}']:
                self.fields[f'{field}_{employee}'] = '0'
        table = [
            ['Travel Time', self.fields[f'travel_time_{employee}']],
            ['Food Allowance', self.fields[f'food_allowance_{employee}']],
            ['Vacation Pay', self.fields[f'vacation_pay_{employee}']],
        ]
        style = [('BACKGROUND', (0, 0), (0, -1), self.colours['grey']),
                 ("VALIGN", (0, 0), (-1, -1), 'MIDDLE')]
        cols = [self.width * .2, self.width * .1]
        self.table(table, style=style, cols=cols)

    def hours_table(self, hours, employee):
        hours_table = [['Day', 'Clock In', 'Clock Out', 'Location']]
        for day, times in hours.items():
            date = datetime.strptime(times[0], '%Y-%m-%d %H:%M:%S')
            date_str = f'{day[:3]} {date.strftime("%b %d %Y")}'
            clock_in = datetime.strptime(times[0], '%Y-%m-%d %H:%M:%S').strftime('%I:%M %p')
            clock_out = datetime.strptime(times[1], '%Y-%m-%d %H:%M:%S').strftime('%I:%M %p')
            location = self.fields[f'{employee}_{day}_location']
            hours_table.append([date_str, clock_in, clock_out, location])
        style = [('BACKGROUND', (0, 0), (-1, 0), self.colours['grey']),
                 ("VALIGN", (0, 0), (-1, -1), 'MIDDLE')]
        self.table(hours_table, style=style)

