from Forms.form import Form


class SafetyTalk(Form):
    name = 'Safety Talk'
    signature_path: str
    separator = 'title'

    def __init__(self):
        super().__init__()

    def print(self):
        self.title('Safety Talk Report Form')
        self.heading(f"Title of Safety Talk:\t{self.fields['title']}")
        self.table([[f"Company: {self.company}", f"Project: {self.fields['location']}"],
                    [f"Talk given by: {self.fields['given_by']}", f"Date: {self.today}"]])
        self.heading('Crew Attending:')
        self.table(self.chunks(self.fields['crew_attending'], 3))
        self.heading('List other topics discussed during the talk: ')
        self.table(self.chunks(self.fields['topics'], 1))
        self.concerns()
        self.signature(f"{self.signature_path}", 'Supervisor')
        self.build()

    def concerns(self):
        concerns_resp = [['Concerns', 'Response/Follow-Up']]
        self.table(concerns_resp, style=False)
        concerns, response = self.level_lists(self.fields['concerns'], self.fields['response'])
        data = list(zip(concerns, response))
        self.table(data)


if __name__ == '__main__':
    form = SafetyTalk()
    form.fields = {'title': 'Safety Talk', 'location': 'Project', 'given_by': 'John Doe',
                       'crew_attending': ['John Doe', 'Jane Doe', 'Joe Doe', 'Jill Doe', 'Jack Doe'],
                       'topics': ['Topic 1', 'Topic 2', 'Topic 3', 'Topic 4', 'Topic 5', 'Topic 6', 'Topic 7'],
                       'concerns': ['Concern 1', 'Concern 2', 'Concern 3', 'Concern 4', 'Concern 5', 'Concern 6'],
                       'response': ['Response 1', 'Response 2', 'Response 3', 'Response 4', 'Response 5',
                                    'Response 6', 'response 7']}
    form.signature_path = 'C:\\Users\\Richard Fitzwell\\Pictures\\signature.jpg'
    form.make_file()
    form.print()
