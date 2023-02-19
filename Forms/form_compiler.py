from Forms.form_fields.form_widgets import (
    SingleOption,
    MultiOptionButton,
    CheckBoxOption,
    SingleOptionButton,
    SingleOptionDatePicker,
)

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Model.main_model import MainModel
    from Controller.form_view_controller import FormViewController
    from Views.Popups.text_field_popup.text_field_popup import TextFieldPopup


class CreateForm:
    def __init__(self, model: 'MainModel', controller: 'FormViewController', form_id: str,
                 popup: 'TextFieldPopup' = None):
        self.model = model
        self.controller = controller
        self.popup = popup
        self.form_ids = [x.lower().replace(' ', '_') for x in self.model.forms]
        self.form_titles = list(self.model.forms)
        self.form_id = form_id
        self.today_form, self.form_title, self.form_id = self.is_today_form()
        self.form_list = self.populate_form_list()

    def populate_form_list(self):
        return [self.add_site, self.add_equipment,
                self.safety_talk_report_form, self.equipment_pre_start_checklist, self.field_level_hazard_assessment]

    def is_today_form(self):
        if self.form_id in self.model.today['forms']:
            return self.form_id, self.model.today['forms'][self.form_id]['name'], \
                   self.model.today['forms'][self.form_id]['name'].lower().replace(' ', '_')
        else:
            return False, self.form_titles[self.form_ids.index(self.form_id)], self.form_id

    def populate_form_view(self):
        return self.form_list[self.form_ids.index(self.form_id)]

    def add_site(self):
        customer = SingleOption(ind='customer', title='Customer/Company', pre_select=[], db=["Add Site", "customer"],
                                controller=self.controller, model=self.model)
        address = SingleOption(ind='address', title='Street Address', pre_select=[], db=["Add Site", "address"],
                               controller=self.controller, model=self.model)
        city = SingleOption(ind='city', title='City', pre_select=[], db=["Add Site", "city"],
                            controller=self.controller, model=self.model)
        start_date = SingleOptionDatePicker(ind='start_date', text='Start Date', model=self.model, time=False,
                                            mandatory=False)
        self.model.form_view_fields['equipment'] = []
        self.model.form_view_fields['blueprints'] = []
        self.model.form_view_fields['pictures'] = []
        self.model.form_view_fields['forms'] = []
        self.controller.view.type = 'site'
        self.remove_save_button()
        return [customer, address, city, start_date]

    def add_equipment(self):
        name = SingleOption(ind='type', title='Type of Equipment', pre_select=[],
                            controller=self.controller, model=self.model)
        site = SingleOption(ind='site', title='Site',
                            pre_select=[f"{self.model.sites[x]['customer']} - {self.model.sites[x]['city']}"
                                        for x in self.model.sites],
                            controller=self.controller, model=self.model)
        mileage = SingleOption(ind='mileage', title='Mileage (Hours)', pre_select=[], mandatory=False,
                               controller=self.controller, model=self.model)
        last_service = SingleOption(ind='last_service', title='Last Service (Mileage)', pre_select=[], mandatory=False,
                                    controller=self.controller, model=self.model)
        last_inspection = SingleOptionDatePicker(ind='last_inspection', text='Last Inspection', model=self.model,
                                                 mandatory=False, time=False)
        unit_num = SingleOption(ind='unit_num', title='Unit Number', pre_select=[],
                                controller=self.controller, model=self.model)
        owned = CheckBoxOption(ind='owned', text='Owned')
        self.fill_in_site(widget=site, key='site')
        self.model.form_view_fields['forms'] = []
        self.model.form_view_fields['pictures'] = []
        self.controller.view.type = 'equipment'
        self.remove_save_button()
        return [name, site, unit_num, mileage, last_service, last_inspection, owned]

    def remove_save_button(self):
        self.controller.view.remove_save_button()

    def fill_in_site(self, widget: 'SingleOption', key: str = 'location'):
        if site_id := self.model.current_site:
            site = f"{self.model.sites[str(site_id)]['customer']} - {self.model.sites[str(site_id)]['city']}"
            widget.add_button_text(site)
            widget.select()
            self.model.form_view_fields[key] = site

    def safety_talk_report_form(self):
        self.controller.view.type = 'forms'
        title = SingleOption(ind='title', title='Title of Safety Talk',
                             pre_select=self.model.forms[self.form_title]['titles'],
                             db=[f"{self.form_title}", 'titles'], divide=True,
                             controller=self.controller, model=self.model)
        project = SingleOption(ind='location', title='Project',
                               pre_select=[f"{self.model.sites[x]['customer']} - {self.model.sites[x]['city']}"
                                           for x in self.model.sites],
                               controller=self.controller, model=self.model)

        self.fill_in_site(project)

        given_by = SingleOption(ind='given_by', title='Who gives the talk',
                                pre_select=self.model.forms[self.form_title]['crew'],
                                db=[f"{self.form_title}", "crew"],
                                controller=self.controller, model=self.model)
        crew_attending = MultiOptionButton(text='Crew Attending', ind='crew_attending', title='Crew Attending',
                                           selections=self.model.forms[self.form_title]['crew'],
                                           db=[f"{self.form_title}", "crew"],
                                           controller=self.controller, model=self.model)
        topics = MultiOptionButton(text='List other topics discussed during the talk', ind='topics',
                                   selections=self.model.forms[self.form_title]['topics'],
                                   db=[f"{self.form_title}", "topics"],
                                   title='List other topics discussed during the talk',
                                   controller=self.controller, model=self.model)
        concerns = MultiOptionButton(text='Concerns', ind='concerns', title='Concerns', mandatory=False,
                                     selections=self.model.forms[self.form_title]['concerns'],
                                     db=[f"{self.form_title}", "concerns"],
                                     controller=self.controller, model=self.model)

        response = MultiOptionButton(text='Response/Follow-Up', ind='response', title='Response/Follow-Up',
                                     selections=self.model.forms[self.form_title]['response'], mandatory=False,
                                     db=[f"{self.form_title}", "response"],
                                     controller=self.controller, model=self.model)

        return [title, project, given_by, crew_attending, topics, concerns, response]

    def equipment_pre_start_checklist(self):
        self.controller.view.type = 'forms'
        location = SingleOption(ind="location", title="Task Location",
                                pre_select=[f"{self.model.sites[x]['customer']} - {self.model.sites[x]['city']}"
                                            for x in self.model.sites],
                                controller=self.controller, model=self.model)
        self.fill_in_site(location)

        machine = SingleOption(ind='machine', title='Machine Make/Model', divide=True,
                               pre_select=[self.model.equipment[x]['type'] for x in
                                           self.model.equipment],
                               controller=self.controller, model=self.model)
        unit_num = SingleOption(ind='unit_num', title='Unit Number', pre_select=[],
                                db=[f"{self.form_title}", "unit_num"],
                                controller=self.controller, model=self.model)
        mileage = SingleOption(ind='mileage', title='Mileage', pre_select=[], db=[f"{self.form_title}", "mileage"],
                               controller=self.controller, model=self.model)

        fluid_levels = MultiOptionButton(text='Fluid Levels', ind='fluid_levels', title='Fluid Levels', equipment=True,
                                         selection_db=self.model.forms[self.form_title]['Fluid Levels'],
                                         controller=self.controller, model=self.model)
        drivers_compartment = MultiOptionButton(text="Driver's Compartment", ind='drivers_compartment',
                                                title="Driver's Compartment", equipment=True,
                                                selection_db=self.model.forms[self.form_title]["Driver's Compartment"],
                                                controller=self.controller, model=self.model)
        body_exterior = MultiOptionButton(text="Body Exterior", ind='body_exterior', title="Body Exterior",
                                          selection_db=self.model.forms[self.form_title]["Body Exterior"], equipment=True,
                                          controller=self.controller, model=self.model)
        under_the_hood = MultiOptionButton(text="Under The Hood", ind='under_the_hood', title="Under The Hood",
                                           selection_db=self.model.forms[self.form_title]["Under The Hood"],
                                           equipment=True,
                                           controller=self.controller, model=self.model)
        undercarriage = MultiOptionButton(text="Undercarriage", ind='undercarriage', title="Undercarriage",
                                          equipment=True, selection_db=self.model.forms[self.form_title]["Undercarriage"],
                                          controller=self.controller, model=self.model)
        brake_tires_wheels = MultiOptionButton(text="Brake, Tires & Wheels", ind='brake_tires_wheels', equipment=True,
                                               title="Brake, Tires & Wheels",
                                               selection_db=self.model.forms[self.form_title]["Brake, Tires & Wheels"],
                                               controller=self.controller, model=self.model)

        return [location, machine, unit_num, mileage, fluid_levels, drivers_compartment, body_exterior, under_the_hood,
                undercarriage, brake_tires_wheels]

    def field_level_hazard_assessment(self):
        self.controller.view.type = 'forms'
        work = SingleOptionButton(ind="work_to_be_done", pre_select=['Concrete', 'Erecting', 'Cladding'],
                                  controller=self.controller)
        task = SingleOption(ind="task", pre_select=[], title="Task", text='Task', divide=True,
                            db=[f"{self.form_title}"],
                            controller=self.controller, model=self.model)
        location = SingleOption(ind="location", title="Task Location",
                                pre_select=[f"{self.model.sites[x]['customer']} - {self.model.sites[x]['city']}"
                                            for x in self.model.sites],
                                controller=self.controller, model=self.model)
        self.fill_in_site(location)
        muster_point = SingleOption(ind="muster_point", title="Muster Point", pre_select=[],
                                    db=[f"{self.form_title}", "muster_point"],
                                    controller=self.controller, model=self.model)
        ppe = CheckBoxOption(ind="ppe_inspected", text="PPE Inspected:")
        items_inspected = MultiOptionButton(ind='items_inspected', selections=[], title='Items Inspected',
                                            text='Items Inspected', mandatory=False,
                                            db=[f"{self.form_title}", "items_inspected"],
                                            controller=self.controller, model=self.model)
        hazards = MultiOptionButton(ind='hazards', selections=[], title='Hazards', text='Hazards',
                                    db=[f"{self.form_title}", "hazards"],
                                    controller=self.controller, model=self.model)
        tool_inspection = CheckBoxOption(ind="tool_inspected",
                                         text="Has a pre-use inspection of tools/equipment been completed?")
        warning_ribbon = CheckBoxOption(ind="warning_ribbon", text="Warning ribbon needed?")
        working_alone = CheckBoxOption(ind="working_alone", text="Is the worker working alone?")
        explanation = SingleOption(ind="explanation", title="If Yes, Explain:", mandatory=False, pre_select=[],
                                   db=[f"{self.form_title}", "explanation"],
                                   controller=self.controller, model=self.model)
        workers = MultiOptionButton(ind="workers", title="Workers", text="Workers",
                                    db=["Safety Talk Report Form", "crew"],
                                    selections=self.model.forms['Safety Talk Report Form']['crew'], signature=True,
                                    controller=self.controller, model=self.model)

        permit_closed = CheckBoxOption(ind="permit_closed", text="Are all Permit(s) closed out?")
        area_cleaned = CheckBoxOption(ind="area_cleaned", text="Was the area cleaned up at the end of job/shift?")
        hazards_remaining = CheckBoxOption(ind="hazards_remaining", text="Are there Hazards remaining?")
        hazard_explanation = SingleOption(ind="hazard_explanation", title="If Yes, Explain:", mandatory=False,
                                          pre_select=[], db=[f"{self.form_title}", "hazard_explanation"],
                                          controller=self.controller, model=self.model)
        incidents = CheckBoxOption(ind="incidents", text="Were there any incidents / injuries?")
        incident_explanation = SingleOption(ind="incident_explanation", title="If Yes, Explain:", mandatory=False,
                                            pre_select=[], db=[f"{self.form_title}", "incident_explanation"],
                                            controller=self.controller, model=self.model)

        return [work, task, location, muster_point, ppe, items_inspected, hazards, tool_inspection,
                warning_ribbon, working_alone, explanation, workers, permit_closed, area_cleaned,
                hazards_remaining, hazard_explanation, incidents, incident_explanation]
