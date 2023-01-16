from Forms.form import Form


class FLHA(Form):
    name = 'Field Level Hazard Assessment'
    signature_path = ''
    client_signature_path = ''
    separator = 'tasks'

    def __init__(self):
        super().__init__()

    def print(self):
        self.title('Field Level Hazard Assessment')
        self.top_info()
        self.heading(f"{self.fields.get('work_to_be_done', '')}: {self.fields.get('task', '')}")
        self.heading('Identify and Prioritize the tasks and hazards below, then identify the plans to '
                     'eliminate/control the hazards.')
        self.add_hazards()
        self.ppe_inspected()
        self.tool_inspection()
        self.warning_ribbon()
        self.working_alone()
        self.heading("Job Completion")
        self.permits()
        self.area_cleaned()
        self.hazards_remaining()
        self.injuries()
        self.workers()
        self.signature(self.signature_path, 'Supervisor')
        self.signature(self.client_signature_path, "Client's Representative")
        self.build()

    def top_info(self):
        data = [[f"Date: {self.date_time}", f"Task Location: {self.fields.get('location', '')}"],
                [f"Muster Point: {self.fields.get('muster_point', '')}",
                 f"Permit Job #: {self.fields.get('permit_number', '')}"]]
        self.table(self.word_wrap_table(data))

    def format_hazard_chart(self):
        risk_plan = [
            [f"{self.fields['risk'][r].get('risk', '')}/{self.fields['risk'][r].get('priority', '')}"
             for r in self.fields.get('hazards', '')],
            [f"{self.fields['plan'].get(r, '')}" for r in self.fields.get('hazards', '')]
        ]
        hazards = self.fields.get('hazards', '')
        risk, plan = self.level_lists(risk_plan[0], risk_plan[1])
        hazards, risk = self.level_lists(hazards, risk)
        hazards, plan = self.level_lists(hazards, plan)
        return list(zip(hazards, risk, plan))

    def add_hazards(self):
        titles = [['Hazard', 'Risk/ Priority', 'Plan to Eliminate/Control']]
        chart = self.format_hazard_chart()
        style = [('BOX', (0, 0), (-1, -1), 1, self.colours['black']),
                 ('INNERGRID', (0, 0), (-1, -1), 0.25, self.colours['black']),
                 ('BACKGROUND', (0, 0), (-1, 0), self.colours['grey']),
                 ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                 ('VALIGN', (0, 0), (-1, 0), 'MIDDLE')]
        self.table(titles + chart, style=style)

    def ppe_inspected(self):
        items = ''
        if self.fields.get('items_inspected', ''):
            items = ", ".join(self.fields.get('items_inspected', ''))
        ppe_inspected_check = self.yes_no(self.fields.get('ppe_inspected', ''))
        ppe = [["PPE Inspected: ", "Yes", ppe_inspected_check[0], "No", ppe_inspected_check[1]]]
        self.table(ppe, cols='yes/no', grid_format='box', spacer=False)
        self.table([["Items Inspected:", f"{items}"]], grid_format='box')

    def tool_inspection(self):
        tools_inspected = self.yes_no(self.fields.get('tools_inspected', ''))
        table = [["Has a pre-use inspection of tools/equipment been completed?",
                  "Yes", tools_inspected[0], "No", tools_inspected[1]]]
        self.table(table, cols='yes/no', grid_format='box', spacer=False)

    def warning_ribbon(self):
        warning_ribbon = self.yes_no(self.fields.get('warning_ribbon', ''))
        table = [["Warning ribbon needed?", "Yes", warning_ribbon[0], "No", warning_ribbon[1]]]
        self.table(table, cols='yes/no', grid_format='box', spacer=False)

    def working_alone(self):
        alone = self.yes_no(self.fields.get('working_alone', ''))
        table = [
            ["Is the worker working alone?", "Yes", alone[0], "No", alone[1]]]
        self.table(table, cols='yes/no', grid_format='box', spacer=False)
        self.table([[f"If yes, explain: {self.fields.get('explanation', '')}"]], grid_format='box')

    def permits(self):
        permits = self.yes_no(self.fields.get('permit_closed', ''))
        table = [["Are all Permit(s) closed out?", "Yes", permits[0], "No", permits[1]]]
        self.table(table, cols='yes/no', grid_format='box', spacer=False)

    def area_cleaned(self):
        area = self.yes_no(self.fields.get('area_cleaned', ''))
        table = [["Was the area cleaned up at end of job/shift?", "Yes", area[0], "No", area[1]]]
        self.table(table, cols='yes/no', grid_format='box', spacer=False)

    def hazards_remaining(self):
        hazards_remaining = self.yes_no(self.fields.get('hazards_remaining', ''))
        table = [["Are there Hazards remaining?",
                  "Yes", hazards_remaining[0], "No", hazards_remaining[1]]]
        self.table(table, cols='yes/no', grid_format='box', spacer=False)
        self.table([["(If Yes, explain):", self.fields.get('hazard_explanation', '')]], grid_format='box')

    def injuries(self):
        incidents = self.yes_no(self.fields.get('incidents', ''))
        table = [["Were there any incidents/injuries?", "Yes", incidents[0], "No", incidents[1]]]
        self.table(table, grid_format='box', cols='yes/no', spacer=False)
        self.table([["If Yes, explain:", self.fields.get('incident_explanation', '')]], grid_format='box')

    def workers(self):
        titles = [["Worker's Name", "Signature", "Initial"]]
        crew = self.fields.get('workers', '')
        signatures = [self.image(f"database/{self.fields['signatures'].get(x, '')}", self.inch(2), self.inch(0.5))
                      for x in self.fields.get('workers', '')]
        initial = [self.image(f"database/{self.fields['initials'].get(x, '')}", self.inch(0.5), self.inch(0.5))
                   for x in self.fields.get('workers', '')]
        if not crew:
            crew = ['']
            signatures = ['']
            initial = ['']
        table = list(zip(crew, signatures, initial))
        cols = [self.inch(2.5), self.inch(2.5), self.inch(1)]
        self.paragraph("Please print and sign below (All Members of the crew) prior to commencing work,"
                       "and initial when task is completed or at the end of the shift.")
        self.table(titles, cols=cols, spacer=False)
        self.table(table, cols=cols)


if __name__ == '__main__':
    fields = {
        "work_to_be_done": "Concrete",
        "task": "Digging",
        "location": "GFL - Pickering",
        "muster_point": "",
        "ppe_inspected": False,
        "items_inspected": "",
        "hazards": "",
        "tool_inspected": False,
        "warning_ribbon": False,
        "working_alone": False,
        "explanation": "",
        "workers": "",
        "permit_closed": False,
        "area_cleaned": False,
        "hazards_remaining": False,
        "hazard_explanation": "",
        "incidents": False,
        "incident_explanation": "",
        "date": "31/12/2022",
        "name": "Field Level Hazard Assessment",
        "risk": {},
        "plan": {},
        "signatures": {},
        "initials": {},
        "site_id": "1",
        "separator": [
            "Digging"
        ],
        "row_text": "Field Level Hazard Assessment 31/12/2022  GFL - Pickering : ['Digging'] ",
        "index": "0"
    }
    form = FLHA()
    form.fields = fields
    form.signature_path = 'C:\\Users\\Richard Fitzwell\\Pictures\\signature.jpg'
    form.make_file()
    form.print()
