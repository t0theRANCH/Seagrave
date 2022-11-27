from os.path import join, dirname

from kivy.lang import Builder

from kivymd.uix.boxlayout import MDBoxLayout


class AddNote(MDBoxLayout):
    pass


Builder.load_file(join(dirname(__file__), "add_note_to_picture.kv"))
