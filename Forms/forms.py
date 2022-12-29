import datetime
import os

from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.units import inch
from reportlab.lib import colors

from Forms.interactivecheckbox import InteractiveCheckBox


class Forms:
    def __init__(self, name, forms, separator, location):
        self.date = datetime.datetime.now()
        self.date_time_string = self.date.strftime('%y_%m%d%_h%m')
        self.date_time = self.date.strftime('%y-%m-%d %h:%m')
        self.name = name
        self.separator = separator
        self.file_name = f"database/forms/{self.name.lower().replace(' ', '_')}_{location}_{self.date_time.replace(' ', '-')}_{separator}"
        self.forms = forms
        self.form_list = self.populate_form_list()
        self.site_id = ''

    def populate_form_list(self):
        return [self.safety_talk, self.equipment_check, self.flha]

    def handle_form_selection(self):
        return self.form_list[self.forms.index(self.name)]

    @staticmethod
    def chunks(l, n):
        n = max(1, n)
        return [l[i:i + n] for i in range(0, len(l), n)]

    def flha(self, fields, signature):
        company = "Seagrave Building Systems"
        work = fields['work_to_be_done']
        site = fields['location']
        muster_point = fields['muster_point']
        permit_number = "90210"
        if fields['items_inspected']:
            items = ",".join(fields['items_inspected'])
        else:
            items = ''
        hazard_chart = [fields['tasks'], fields['hazards']]
        tasks = ['Tasks'] + fields['tasks']
        hazards = ['Hazards'] + fields['hazards']
        risk = ["RISK/\nPRIORITY"] + [f"{fields['risk'][r]['risk']}/{fields['risk'][r]['priority']}" for r in fields['hazards']]
        plan = ['PLANS TO ELIMINATE/CONTROL'] + [f"{fields['plan'][r]}" for r in fields['hazards']]

        explanation = fields['explanation']
        hazards_remaining = fields['hazard_explanation']
        incident_explanation = fields["incident_explanation"]

        crew = ["Worker's Name (Print)"] + fields['workers']
        signatures = [Image(f"database/{fields['signatures'][x]}", 2 * inch, 0.5 * inch)
                      for x in fields['workers']]
        initial = [Image(f"database/{fields['initials'][x]}", 0.5 * inch, 0.5 * inch)
                   for x in fields['workers']]
        signatures.insert(0, "Signature")
        initial.insert(0, "Initial")
        pdf = SimpleDocTemplate(f"{self.file_name}.pdf")
        flowables = []
        style_sheet = getSampleStyleSheet()
        title = [["Field Level Hazard Assessment", f"Company Name: {company}"]]
        t1 = Table(title, hAlign='LEFT', colWidths=3.25 * inch)
        t1.setStyle(TableStyle([('BOX', (-1, -1), (-1, -1), 1, colors.black)
                                ]))
        flowables.append(t1)

        w = [[f"Work to be done: {work}", f"Date:{self.date_time}"],
             [f"Task Location: {site}    Muster Point: {muster_point}", f"Permit Job #: {permit_number}"]]
        t2 = Table(w, hAlign='LEFT', colWidths=[5 * inch, 1.5 * inch])
        t2.setStyle(TableStyle([('BOX', (0, 0), (-1, -1), 1, colors.black),
                                ('LINEBEFORE', (-1, 0), (-1, -1), 1, colors.black),
                                ('LINEBELOW', (0, 0), (-1, -1), 1, colors.black)
                                ]))
        flowables.append(t2)

        if fields['ppe_inspected']:
            ppe_yes = InteractiveCheckBox(name='Yes', checked=True, tooltip="Yes")
            ppe_no = InteractiveCheckBox(name='No', checked=False, tooltip="No")
        else:
            ppe_yes = InteractiveCheckBox(name='Yes', checked=False, tooltip="Yes")
            ppe_no = InteractiveCheckBox(name='No', checked=True, tooltip="No")

        ppe = [["PPE Inspected: ", ppe_yes, "Yes", ppe_no, "No", f"Items Inspected: {items}"]]
        t3 = Table(ppe, hAlign='LEFT', colWidths=[1 * inch, 0.3 * inch, 0.3 * inch, 0.3 * inch, 0.3 * inch, 4.3 * inch])
        t3.setStyle(TableStyle([('BOX', (0, 0), (-1, -1), 1, colors.black)]))
        flowables.append(t3)
        flowables.append(Paragraph('Identify and Prioritize the tasks and hazards below, then identify the plans to '
                                   'eliminate/control the hazards.', style_sheet['Heading6']))
        l = [tasks, hazards, risk, plan]
        for _ in range(len(hazard_chart)+1):
            for each in l:
                if len(each) < len(hazard_chart) + 2:
                    each.append('')

        task_chart = [[f"{tasks[n]}", f"{hazards[n]}", f"{risk[n]}", f"{plan[n]}"] for n in range(len(hazard_chart)+2)]
        t4 = Table(task_chart, hAlign='LEFT', colWidths=[2 * inch, 2 * inch, 0.5 * inch, 2 * inch])
        t4.setStyle(TableStyle([('BOX', (0, 0), (-1, -1), 1, colors.black),
                                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                                ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
                                ('FONTSIZE', (2, 0), (2, 0), 6),
                                ('FONTSIZE', (-1, 0), (-1, 0), 8)]))
        flowables.append(t4)

        if fields['tool_inspected']:
            tool_yes = InteractiveCheckBox(name='Yes', checked=True, tooltip="Yes")
            tool_no = InteractiveCheckBox(name='No', checked=False, tooltip="No")
        else:
            tool_yes = InteractiveCheckBox(name='Yes', checked=False, tooltip="Yes")
            tool_no = InteractiveCheckBox(name='No', checked=True, tooltip="No")

        if fields['warning_ribbon']:
            ribbon_yes = InteractiveCheckBox(name='Yes', checked=True, tooltip="Yes")
            ribbon_no = InteractiveCheckBox(name='No', checked=False, tooltip="No")
        else:
            ribbon_yes = InteractiveCheckBox(name='Yes', checked=False, tooltip="Yes")
            ribbon_no = InteractiveCheckBox(name='No', checked=True, tooltip="No")

        tools = [["Has a pre-use inspection of tools/equipment been completed?", "Yes", tool_yes, "No", tool_no,
                  "Warning ribbon needed?", "Yes", ribbon_yes, "No", ribbon_no]]
        t5 = Table(tools, hAlign='LEFT',
                   colWidths=[2.5 * inch, 0.3 * inch, 0.3 * inch, 0.3 * inch, 0.55 * inch, 1.35 * inch,
                              0.3 * inch, 0.3 * inch, 0.3 * inch, 0.3 * inch])
        t5.setStyle(TableStyle([('BOX', (0, 0), (-1, -1), 1, colors.black),
                                ('LINEBEFORE', (5, 0), (5, 0), 1, colors.black),
                                ('FONTSIZE', (0, 0), (-1, 0), 6)]))
        flowables.append(t5)

        a = [["Is the worker working alone?", "If Yes, explain:"]]
        t6 = Table(a, hAlign='LEFT', colWidths=[2.25 * inch, 4.25 * inch])
        t6.setStyle(TableStyle([('LINEBEFORE', (0, 0), (-1, 0), 1, colors.black),
                                ('LINEAFTER', (0, 0), (-1, 0), 1, colors.black)]))
        flowables.append(t6)

        if fields['working_alone']:
            alone_yes = InteractiveCheckBox(name='Yes', checked=True, tooltip="Yes")
            alone_no = InteractiveCheckBox(name='No', checked=False, tooltip="No")
        else:
            alone_yes = InteractiveCheckBox(name='Yes', checked=False, tooltip="Yes")
            alone_no = InteractiveCheckBox(name='No', checked=True, tooltip="No")

        alone = [["Yes", alone_yes, "No", alone_no, f"{explanation}"]]
        t7 = Table(alone, hAlign='LEFT', colWidths=[0.3 * inch, 0.3 * inch, 0.3 * inch, 1.35 * inch, 4.25 * inch])
        t7.setStyle(TableStyle([('LINEBEFORE', (0, 0), (0, 0), 1, colors.black),
                                ('LINEBEFORE', (-1, 0), (-1, 0), 1, colors.black),
                                ('LINEAFTER', (-1, 0), (-1, 0), 1, colors.black)]))
        flowables.append(t7)

        t8 = Table([["Job Completion"]], hAlign='LEFT', colWidths=6.5 * inch)
        t8.setStyle(TableStyle([('BOX', (0, 0), (-1, -1), 1, colors.black)]))
        flowables.append(t8)

        if fields['permit_closed']:
            permit_yes = InteractiveCheckBox(name='Yes', checked=True, tooltip="Yes")
            permit_no = InteractiveCheckBox(name='No', checked=False, tooltip="No")
        else:
            permit_yes = InteractiveCheckBox(name='Yes', checked=False, tooltip="Yes")
            permit_no = InteractiveCheckBox(name='No', checked=True, tooltip="No")

        if fields['hazards_remaining']:
            hazard_yes = InteractiveCheckBox(name='Yes', checked=True, tooltip="Yes")
            hazard_no = InteractiveCheckBox(name='No', checked=False, tooltip="No")
        else:
            hazard_yes = InteractiveCheckBox(name='Yes', checked=False, tooltip="Yes")
            hazard_no = InteractiveCheckBox(name='No', checked=True, tooltip="No")

        permits = [["Are all Permit(s) closed out?", "Yes", permit_yes, "No", permit_no, "Are there Hazards remaining?",
                    "Yes", hazard_yes, "No", hazard_no, "(If Yes, explain)"]]
        t9 = Table(permits, hAlign='LEFT', colWidths=[1.9 * inch, 0.3 * inch, 0.3 * inch, 0.3 * inch, 0.3 * inch,
                                                      1.2 * inch, 0.25 * inch, 0.25 * inch, 0.25 * inch, 0.25 * inch,
                                                      1.2 * inch])
        t9.setStyle(TableStyle([('LINEBEFORE', (0, 0), (0, 0), 1, colors.black),
                                ('LINEBEFORE', (5, 0), (5, 0), 1, colors.black),
                                ('LINEAFTER', (-1, 0), (-1, 0), 1, colors.black),
                                ('LINEBELOW', (0, 0), (4, 0), 1, colors.black),
                                ('FONTSIZE', (0, 0), (-1, -1), 6)]))
        flowables.append(t9)

        if fields['area_cleaned']:
            clean_yes = InteractiveCheckBox(name='Yes', tooltip='Yes', checked=True)
            clean_no = InteractiveCheckBox(name='No', tooltip='No', checked=False)
        else:
            clean_yes = InteractiveCheckBox(name='Yes', tooltip='Yes', checked=False)
            clean_no = InteractiveCheckBox(name='No', tooltip='No', checked=True)
        work_area = [
            ["Was the area cleaned up at end of job/shift?", "Yes", clean_yes, "No", clean_no, hazards_remaining]]
        t10 = Table(work_area, hAlign='LEFT', colWidths=[1.9 * inch, 0.3 * inch, 0.3 * inch, 0.3 * inch, 0.3 * inch,
                                                         3.4 * inch])
        t10.setStyle(TableStyle([('LINEBEFORE', (0, 0), (0, 0), 1, colors.black),
                                 ('LINEBEFORE', (5, 0), (5, 0), 1, colors.black),
                                 ('LINEAFTER', (-1, 0), (-1, 0), 1, colors.black),
                                 ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
                                 ('FONTSIZE', (0, 0), (-1, -1), 6)]))
        flowables.append(t10)

        i = [["Were there any incidents/injuries?", "If Yes, explain:"]]
        t11 = Table(i, colWidths=[2.25 * inch, 4.25 * inch], hAlign='LEFT')
        t11.setStyle(TableStyle([('LINEBEFORE', (0, 0), (-1, 0), 1, colors.black),
                                 ('LINEAFTER', (-1, 0), (-1, 0), 1, colors.black)]))
        flowables.append(t11)

        if fields['incidents']:
            injury_yes = InteractiveCheckBox(name='Yes', tooltip='Yes', checked=True)
            injury_no = InteractiveCheckBox(name='No', tooltip='No', checked=False)
        else:
            injury_yes = InteractiveCheckBox(name='Yes', tooltip='Yes', checked=False)
            injury_no = InteractiveCheckBox(name='No', tooltip='No', checked=True)

        injury = [["Yes", injury_yes, "No", injury_no, incident_explanation]]
        t12 = Table(injury, colWidths=[0.3 * inch, 0.3 * inch, 0.3 * inch, 1.35 * inch, 4.25 * inch], hAlign='LEFT')
        t12.setStyle(TableStyle([('LINEBEFORE', (0, 0), (0, 0), 1, colors.black),
                                 ('LINEBEFORE', (-1, 0), (-1, 0), 1, colors.black),
                                 ('LINEAFTER', (-1, 0), (-1, 0), 1, colors.black),
                                 ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black)]))
        flowables.append(t12)
        flowables.append(Paragraph("Please print and sign below (All Members of the crew) prior to commencing work,"
                                   "and initial when task is completed or at the end of the shift.",
                                   style_sheet['Normal']))

        workers = [[f"{crew[n]}", signatures[n], initial[n]] for n in range(len(crew))]
        t13 = Table(workers, hAlign='LEFT', colWidths=[2.75 * inch, 2.75 * inch, 1 * inch])
        t13.setStyle(TableStyle([('BOX', (0, 0), (-1, -1), 1, colors.black),
                                 ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black)]))
        flowables.append(t13)
        flowables.append(Spacer(1, 12))
        a = Image(f"database/{signature}", 2 * inch, 0.5 * inch)
        foreman = [["Foreperson's Name and Signature (Sign upon reviewing completed card): ", a]]
        t14 = Table(foreman, hAlign='LEFT')
        t14.setStyle(TableStyle([('LINEBELOW', (-1, 0), (-1, 0), 1, colors.black),
                                 ('FONTSIZE', (0, 0), (0, 0), 8)]))
        flowables.append(t14)

        flowables.append(Spacer(1, 12))
        client = [["Client's Representative (Review) signature:", a]]
        t15 = Table(client, hAlign='LEFT')
        t15.setStyle(TableStyle([('LINEBELOW', (-1, 0), (-1, 0), 1, colors.black),
                                 ('FONTSIZE', (0, 0), (0, 0), 8)]))
        flowables.append(t15)
        pdf.build(flowables)
        signatures = [fields['signatures'][x] for x in fields['workers']]
        initials = [fields['initials'][x] for x in fields['workers']]
        for s in (signatures + initials):
            os.remove(f"database/{s}")
        os.remove(f"database/{self.name}_{self.separator}_screenshot.png")

    def safety_talk(self, fields, signature):
        company = 'Seagrave Building Systems'
        conc_resp = [['Concerns', 'Response/Follow-Up']]
        a = Image(f"{os.getcwd()}/database/{signature}", 2 * inch, 0.5 * inch)

        if len(fields['concerns']) >= len(fields['response']):
            n = 'concerns'
            n2 = 'response'
        else:
            n = 'response'
            n2 = 'concerns'
        for num, x in enumerate(fields[n], 0):
            if num < len(fields[n2]):
                conc_resp.append([x, fields[n2][num]])
            else:
                conc_resp.append([x, ''])

        pdf = SimpleDocTemplate(f"{self.file_name}.pdf")
        flowables = []
        style_sheet = getSampleStyleSheet()
        crew = Paragraph("Crew Attending: ", style_sheet['Normal'])
        crew_list = self.chunks(fields['crew_attending'], 3)
        topic_list = self.chunks(fields['topics'], 1)
        today = str(datetime.date.today())

        flowables.append(Paragraph('Safety talk Report Form', style_sheet['Title']))
        flowables.append(Spacer(1, 12))
        flowables.append(Paragraph("Title of Safety Talk: <u>{}</u>".format(fields['title']), style_sheet['Normal']))

        data1 = [["Company: {}".format(company), "Project: {}".format(fields['location'])],
                 ["Talk given by: {}".format(fields['given_by']), "Date: {}".format(today)]]

        t1 = Table(data1, hAlign='LEFT', colWidths=3 * inch)
        t1.setStyle(TableStyle([('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                                ('LINEABOVE', (0, 1), (-1, -1), 1, colors.black),
                                ('LINEBEFORE', (1, 0), (1, 1), 1, colors.black)
                                ]))

        flowables.append(Spacer(1, 12))
        flowables.append(t1)
        flowables.append(Spacer(1, 12))
        flowables.append(crew)
        flowables.append(Spacer(1, 12))
        t2 = Table(crew_list, hAlign='LEFT', colWidths=2 * inch)
        t2.setStyle(TableStyle([('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black)
                                ]))
        flowables.append(t2)
        flowables.append(Spacer(1, 12))
        flowables.append(Paragraph("List other topics discussed during the talk: ", style_sheet['Normal']))
        t3 = Table(topic_list, hAlign='LEFT', colWidths=6 * inch)
        t3.setStyle(TableStyle([('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black)
                                ]))
        flowables.append(Spacer(1, 12))
        flowables.append(t3)
        flowables.append(Spacer(1, 12))
        t4 = Table(conc_resp, hAlign='LEFT', colWidths=3 * inch)
        t4.setStyle(TableStyle([('BOX', (0, 1), (-1, -1), 0.25, colors.black),
                                ('INNERGRID', (0, 1), (-1, -1), 0.25, colors.black)
                                ]))
        flowables.append(Spacer(1, 12))
        flowables.append(t4)
        flowables.append(Spacer(1, 12))

        if 'Andrew' in fields['given_by']:
            given_by_title = 'Health & Safety Rep'
        else:
            given_by_title = 'Supervisor'

        footer = [["Signed: ", a, "Title", given_by_title]]
        t5 = Table(footer, hAlign='LEFT')
        t5.setStyle(TableStyle([('LINEBELOW', (1, 0), (1, 0), 1, colors.black),
                                ('LINEBELOW', (3, 0), (3, 0), 1, colors.black)
                                ]))
        flowables.append(t5)
        pdf.build(flowables)
        os.remove(f"database/{self.name}_{self.separator}_screenshot.png")

    def equipment_check(self, fields, signature):
        work_required = []
        assigned_to = []
        completion = []
        if len(fields.keys()) > 15:
            for key, value in fields.items():
                if "work_required" in key:
                    a = key.replace("work_required", "assigned_to")
                    c = key.replace("work_required", "completion")
                    work_required.append(value)
                    assigned_to.append(fields[a])
                    completion.append(fields[c])
        else:
            work_required.append('')
            work_required.append('')
            assigned_to.append('')
            assigned_to.append('')
            completion.append('')
            completion.append('')

        company = 'Seagrave Building Systems'
        if 'signatures' in fields:
            repairman_signature = Image(f"database/{fields['signatures']['Repairman']}", 1.5 * inch, 0.5 * inch)
        else:
            repairman_signature = ''

        supervisor_signature = Image(f"database/{signature}", 1.5 * inch, 0.5 * inch)

        pdf = SimpleDocTemplate(f"{self.file_name}.pdf")
        flowables = []
        style_sheet = getSampleStyleSheet()

        flowables.append(Paragraph('Equipment/Vehicle Pre-Start Checklist', style_sheet['Title']))

        header = [["Company: {}".format(company), "Machine Make/Model: {}".format(fields['machine'])]]
        t1 = Table(header, hAlign='LEFT', colWidths=3.125 * inch)
        t1.setStyle(TableStyle([('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                                ('LINEBEFORE', (1, 0), (1, 0), 1, colors.black),
                                ]))
        header2 = [["Unit #: {}".format(fields['unit_num']), "Date & Time: {}".format(self.date_time),
                    "Mileage: {}".format(fields['mileage'])]]
        t2 = Table(header2, hAlign='LEFT', colWidths=[1.85 * inch, 2.55 * inch, 1.85 * inch])
        t2.setStyle(TableStyle([('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                                ('LINEBEFORE', (1, 0), (1, 0), 1, colors.black),
                                ('LINEBEFORE', (2, 0), (2, 0), 1, colors.black),
                                ]))

        flowables.append(t1)
        flowables.append(t2)
        flowables.append(Spacer(1, 12))
        flowables.append(Paragraph("Rating Legend", style_sheet['Heading4']))

        legend = [[Paragraph("<b>NA</b> - Not Applicable"), Paragraph("<b>P</b> - Passed in good working condition")],
                  [Paragraph("<b>M</b> - Passed but maintenance required"),
                   Paragraph("<b>R</b> - Rejected, repair necessary before returning to service")]]
        t3 = Table(legend, hAlign='LEFT', colWidths=[2.6 * inch, 3.7 * inch])
        t3.setStyle(TableStyle([('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                                ('LINEBEFORE', (1, 0), (1, 1), 1, colors.black),
                                ]))
        flowables.append(t3)

        flowables.append(Spacer(1, 12))

        def combine_lists(heading_name):
            final_list = []
            for x in reversed(fields[heading_name].keys()):
                final_list.extend((fields[heading_name][x], x))
            return final_list

        flowables.append(Paragraph("Fluid Levels", style_sheet['Heading4']))

        fluid_levels_master = combine_lists('fluid_levels')
        fluid_levels = self.chunks(fluid_levels_master, 6)
        t4 = Table(fluid_levels, hAlign='LEFT',
                   colWidths=[0.3 * inch, 1.8 * inch, 0.3 * inch, 1.8 * inch, 0.3 * inch, 1.8 * inch])
        t4.setStyle(TableStyle([('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black)
                                ]))
        flowables.append(t4)

        flowables.append(Spacer(1, 12))

        drivers_compartment_master = combine_lists('drivers_compartment')
        drivers_compartment = self.chunks(drivers_compartment_master, 6)
        flowables.append(Paragraph("Driver's Compartment", style_sheet['Heading4']))
        t5 = Table(drivers_compartment, hAlign='LEFT',
                   colWidths=[0.3 * inch, 1.8 * inch, 0.3 * inch, 1.8 * inch, 0.3 * inch, 1.8 * inch])
        t5.setStyle(TableStyle([('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black)
                                ]))
        flowables.append(t5)

        flowables.append(Spacer(1, 12))

        body_exterior_master = combine_lists('body_exterior')
        body_exterior = self.chunks(body_exterior_master, 6)
        flowables.append(Paragraph("Body Exterior", style_sheet['Heading4']))

        t6 = Table(body_exterior, hAlign='LEFT',
                   colWidths=[0.3 * inch, 1.8 * inch, 0.3 * inch, 1.8 * inch, 0.3 * inch, 1.8 * inch])
        t6.setStyle(TableStyle([('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black)
                                ]))
        flowables.append(t6)

        flowables.append(Spacer(1, 12))

        under_the_hood_master = combine_lists('under_the_hood')
        under_the_hood = self.chunks(under_the_hood_master, 6)
        flowables.append(Paragraph("Under The Hood", style_sheet['Heading4']))
        t7 = Table(under_the_hood, hAlign='LEFT',
                   colWidths=[0.3 * inch, 1.8 * inch, 0.3 * inch, 1.8 * inch, 0.3 * inch, 1.8 * inch])
        t7.setStyle(TableStyle([('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black)
                                ]))
        flowables.append(t7)

        flowables.append(Spacer(1, 12))

        undercarriage_master = combine_lists('undercarriage')
        undercarriage = self.chunks(undercarriage_master, 6)
        flowables.append(Paragraph("Undercarriage", style_sheet['Heading4']))

        t8 = Table(undercarriage, hAlign='LEFT',
                   colWidths=[0.3 * inch, 1.8 * inch, 0.3 * inch, 1.8 * inch, 0.3 * inch, 1.8 * inch])
        t8.setStyle(TableStyle([('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black)
                                ]))
        flowables.append(t8)

        flowables.append(Spacer(1, 12))
        brake_tire_wheels_master = combine_lists('brake_tires_wheels')
        brake_tire_wheels = self.chunks(brake_tire_wheels_master, 6)
        flowables.append(Paragraph("Brake, Tires, and Wheels", style_sheet['Heading4']))

        t9 = Table(brake_tire_wheels, hAlign='LEFT',
                   colWidths=[0.3 * inch, 1.8 * inch, 0.3 * inch, 1.8 * inch, 0.3 * inch, 1.8 * inch])
        t9.setStyle(TableStyle([('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black)
                                ]))
        flowables.append(t9)
        ffc = InteractiveCheckBox(name='passed', checked=True, tooltip="Pass")
        failure = InteractiveCheckBox(name='not_passed', tooltip='Fail')
        passed = [[ffc, "Equipment Passed", failure, "Equipment Not Passed"]]
        t10 = Table(passed, hAlign='LEFT', colWidths=[0.25 * inch, 1.6 * inch, 0.25 * inch, 1.6 * inch])
        t10.setStyle(TableStyle([('ALIGN', (1, 0), (1, 0), 'LEFT'),
                                 ('ALIGN', (-1, 0), (-1, 0), 'LEFT')
                                 ]))
        flowables.append(Spacer(1, 12))
        flowables.append(t10)
        flowables.append(Spacer(1, 12))

        actions = [['Work Required', 'Assigned To', 'Completion (Date/Time)']]
        t11 = Table(actions, hAlign='LEFT', colWidths=2.15 * inch)
        flowables.append(t11)
        actions_2 = []
        for i, (w, a, c) in enumerate(zip(work_required, assigned_to, completion), start=1):
            actions_2.append([f"{i}.", f"{w}", f"    {i}.", f"{a}", f"    {i}.", f"{c}"])

        t12 = Table(actions_2, hAlign='LEFT',
                    colWidths=[0.25 * inch, 1.75 * inch, 0.4 * inch, 1.75 * inch, 0.4 * inch, 1.75 * inch])
        t12.setStyle(TableStyle([('LINEBELOW', (1, 0), (1, -1), 1, colors.black),
                                 ('LINEBELOW', (3, 0), (3, -1), 1, colors.black),
                                 ('LINEBELOW', (5, 0), (5, -1), 1, colors.black)
                                 ]))

        flowables.append(t12)

        signature = [['Repairman Signature: ', repairman_signature, "Supervisor's Signature: ", supervisor_signature]]
        t13 = Table(signature, hAlign='LEFT', colWidths=[1.5 * inch, 1.6 * inch, 1.6 * inch, 1.6 * inch])
        t13.setStyle(TableStyle([('LINEBELOW', (1, 0), (1, 0), 1, colors.black),
                                 ('LINEBELOW', (-1, 0), (-1, 0), 1, colors.black)
                                 ]))

        flowables.append(Spacer(1, 12))
        flowables.append(t13)
        pdf.build(flowables)
        os.remove(f"database/{self.name}_{self.separator}_screenshot.png")
        if 'signatures' in fields:
            os.remove(f"database/{self.name}_{self.separator}_Repairman_Sign.png")


