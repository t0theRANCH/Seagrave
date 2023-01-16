from Forms.form import Form


class EquipmentChecklist(Form):
    name = 'Equipment/Vehicle Pre-Start Checklist'
    signature_path = ''
    separator = 'machine'
    categories = {'Fluid Levels': 'fluid_levels', "Driver's Compartment": 'drivers_compartment',
                  'Body Exterior': 'body_exterior', 'Under The Hood': 'under_the_hood',
                  'Undercarriage': 'undercarriage', "Brake, Tires, and Wheels": 'brake_tires_wheels'}
    work_required = []
    assigned_to = []
    completion = []

    def __init__(self):
        super().__init__()
        self.checklist_col_widths = [self.inch(0.3), self.inch(1.8), self.inch(0.3), self.inch(1.8), self.inch(0.3),
                                     self.inch(1.8)]
        self.repair_col_widths = [self.inch(0.25), self.inch(1.75), self.inch(0.4), self.inch(1.75), self.inch(0.4),
                                  self.inch(1.75)]
        self.do_repairs = self.is_repairs()
        self.format_repairs()
        self.signatures = {}

    def is_repairs(self):
        return len(self.fields.keys()) > 15

    def format_repairs(self):
        if self.do_repairs:
            self.add_repairs()
            return
        self.add_lines()

    def add_lines(self, lines=None):
        if not lines:
            lines = [('', ''), ('', ''), ('', '')]
        self.work_required.extend(lines[0])
        self.assigned_to.extend(lines[1])
        self.completion.extend(lines[2])

    def add_repairs(self):
        for key, value in self.fields.items():
            if "work_required" in key:
                self.add_lines(([value],
                                [self.fields[key.replace("work_required", "assigned_to")]],
                                [self.fields[key.replace("work_required", "completion")]])
                               )

    def combine_lists(self, heading_name):
        final_list = []
        for x in reversed(self.fields[heading_name].keys()):
            final_list.extend((self.fields[heading_name][x], x))
        return final_list

    def format_list(self, heading_name):
        master = self.combine_lists(heading_name)
        return self.chunks(master, 6)

    def print(self):
        self.title('Equipment/Vehicle Pre-Start Checklist')
        self.top_info()
        self.rating_legend()
        self.grades()
        self.equipment_passed()
        self.repairs()
        self.add_signatures()
        self.build()

    def top_info(self):
        self.table([[f"Company: {self.company}", f"Machine Make/Model: {self.fields['machine']}"]], spacer=False)
        self.table([[f"Unit #: {self.fields['unit_num']}",
                     f"Date & time: {self.date_time}",
                     f"Mileage: {self.fields['mileage']}"]])

    def rating_legend(self):
        self.heading('Rating Legend')
        legend = [["<b>NA</b> - Not Applicable", "<b>P</b> - Passed in good working condition"],
                  ["<b>M</b> - Passed but maintenance required",
                   "<b>R</b> - Rejected, repair necessary before returning to service"]]
        self.table(data=self.word_wrap_table(legend), grid_format='grid_no_underline')

    def grades(self):
        for heading, key in self.categories.items():
            self.heading(heading)
            self.table(self.format_list(key), cols=self.checklist_col_widths)

    def equipment_passed(self):
        yes_no = self.yes_no(self.is_repairs())
        passed = [[yes_no[0], "Equipment Passed", yes_no[1], "Equipment Not Passed"]]
        style = [('ALIGN', (1, 0), (1, 0), 'LEFT'), ('ALIGN', (-1, 0), (-1, 0), 'LEFT')]
        self.table(passed, cols=[self.inch(0.3), self.inch(2.6), self.inch(0.3), self.inch(2.6)], style=style)

    def repairs(self):
        actions = [['Work Required', 'Assigned To', 'Completion (Date/Time)']]
        self.table(actions, style=False, spacer=False)
        actions_2 = [[f"{i}.", f"{w}", f"    {i}.", f"{a}", f"    {i}.", f"{c}"] for i, (w, a, c) in
                     enumerate(zip(self.work_required, self.assigned_to, self.completion), start=1)]
        style = [('LINEBELOW', (1, 0), (1, -1), 1, self.colours['black']),
                 ('LINEBELOW', (3, 0), (3, -1), 1, self.colours['black']),
                 ('LINEBELOW', (5, 0), (5, -1), 1, self.colours['black'])
                 ]
        self.table(actions_2, cols=self.repair_col_widths, style=style)

    def get_signatures(self):
        if 'signatures' in self.fields:
            self.signatures = {'Repairman': f"database/{self.fields['signatures']['Repairman']}",
                               'Supervisor': self.signature_path}
            return
        self.signatures = {'Repairman': '', 'Supervisor': self.signature_path}

    def add_signatures(self):
        self.get_signatures()
        for person, signature in self.signatures.items():
            self.signature(signature, person)


if __name__ == '__main__':
    fields = {
        "name": "Equipment and Vehicle Pre-Start Checklist",
        "unit_num": "69",
        "mileage": "9001",
        "machine": "Ford F-150",
        "location": "The Moon",
        "fluid_levels": {
            "Motor Oil": "P",
            "Rear End": "P",
            "Air Filter": "P",
            "Radiator": "P",
            "Brake Fluid": "P",
            "Oil Change Required?": "P",
            "Power Steering": "P",
            "Greasing Required": "P",
            "Oil Filter Changed?": "P",
            "Windshield Washer": "P"
        },
        "drivers_compartment": {
            "Sun Visors": "P",
            "Horns & Switches": "P",
            "Steering Power Assist": "P",
            "Windshield Wipers": "P",
            "Windshield Defrost": "P",
            "Windshield": "P",
            "Side Windows": "P",
            "Beam Indicator": "P",
            "Instrument Lamps": "P",
            "Pedal Pads": "P",
            "Fire Extinguisher": "P",
            "Hazard Warning Kit/Flares": "P",
            "Seats & Seatbelts": "P",
            "First Aid Kit": "P",
            "Air Pressure Gauge": "P",
            "Speedometer": "P",
            "Survival Kit": "P",
            "Cell Phone": "P",
            "Compressor Buildups": "P",
            "Acc. Pedal and Air Throttle": "P",
            "Booster Cable": "P",
            "Air Leakage": "P",
            "Compressed Air": "P",
            "Steering Column Security": "P"
        },
        "body_exterior": {
            "Head Lamp Operation/Aim": "P",
            "Clearance Lamps": "P",
            "Identification Lamps": "P",
            "Tail Lamps": "P",
            "Stop Lamps": "P",
            "Turn Signal Lamps": "P",
            "Marker Lamps": "P",
            "Hazard Lamps": "P",
            "Reflex Reflectors": "P",
            "Trailer Hitch": "P",
            "TDG Placards": "P",
            "Fenders/Mud Flaps": "P",
            "Trailer Cord": "P",
            "Paint": "P",
            "Air Lines": "P",
            "Tire Pressure": "P",
            "Headache Rack or Chain": "P",
            "Body & Doors": "P",
            "Glad Hands & Air Systems": "P",
            "Reservoirs/Brackets/Straps": "P",
            "Bumpers & Cabs": "P"
        },
        "under_the_hood": {
            "Hood": "P",
            "Air Compressor Belt": "P",
            "Air Compressor": "P",
            "Power Steering System": "P",
            "Fuel Pump & System": "P",
            "Battery & Wiring": "P",
            "Air Filter": "P",
            "Fan & Belt": "P",
            "Carburetor": "P",
            "Cooling System": "P",
            "Windshield Washer Pump": "P",
            "Distributor": "P",
            "Exhaust System": "P",
            "Windshield Wash Container": "P"
        },
        "undercarriage": {
            "Pin & Bushing Wear": "P",
            "Sprocket": "P",
            "Springs": "P",
            "Link Wear": "P",
            "Shock Absorbers": "P",
            "Muffler": "P",
            "Roller Wear": "P",
            "Oil Pan": "P",
            "Pittman Arm": "P",
            "Idler Wear": "P",
            "Drag Link": "P",
            "Differential": "P",
            "Track Wear": "P",
            "Tie Rod": "P",
            "Suspension": "P",
            "Roller Guards": "P",
            "Frame Rails": "P",
            "Axles": "P"
        },
        "brake_tires_wheels": {
            "Brake Components": "P",
            "Chock Block": "P",
            "Road Clearance": "P",
            "Spring Caging Bolts": "P",
            "Brake Drum Condition": "P",
            "Brake Lining Thickness": "P",
            "Disc Brakes": "P",
            "Brake Lines & Hoses": "P",
            "Brake Failure Indicator": "P",
            "Reservoirs & Valves": "P",
            "Tire Pressure": "P",
            "Park Brake": "P",
            "Wheel Bearings": "P",
            "Vacuum System Reserve": "P",
            "Emergency Brake": "P",
            "Proportioning Valve": "P",
            "Pump Operator": "P",
            "Brake Operation": "P",
            "Brake Camshafts & Travel": "P",
            "Tire Wear": "P",
            "Jack": "P",
            "Tire Iron": "P",
            "Spare Tire": "P",
            "Chains": "P"
        }
    }
    form = EquipmentChecklist()
    form.fields = fields
    form.signature_path = 'C:\\Users\\Richard Fitzwell\\Pictures\\signature.jpg'
    form.make_file()
    form.print()
