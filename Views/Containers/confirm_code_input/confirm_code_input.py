import time

from kivy.metrics import dp
from kivy.properties import NumericProperty
from kivy.uix.behaviors import FocusBehavior, ButtonBehavior

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel


class NumberLabel(ButtonBehavior, MDLabel):
    def __init__(self, index, container, **kwargs):
        super(NumberLabel, self).__init__(**kwargs)
        self.id = str(index)
        self.container = container
        self.size_hint_x = 1/6
        self.height = dp(24)
        self.font_size = dp(24)
        self.text = "*"

    def on_release(self):
        if self.container.last_box:
            self.container.last_box = self.container.current_box
        self.container.current_box = int(self.id)


class NumberInput(FocusBehavior, MDBoxLayout):
    current_box = NumericProperty(allownone=True)
    last_box = NumericProperty(allownone=True)
    last_press_time = 0

    def __init__(self, **kwargs):
        super(NumberInput, self).__init__(**kwargs)
        self.input_type = 'number'
        self.is_focusable = True
        self.input_boxes = []
        self.populate_input_boxes()

    def populate_input_boxes(self):
        for num in range(6):
            n = NumberLabel(index=num, container=self)
            self.add_widget(n)
            self.input_boxes.append(n)

    def keyboard_on_key_up(self, window, keycode):
        current_time = time.time()
        if current_time - self.last_press_time < 0.1:
            return True
        self.last_press_time = current_time
        if keycode[1] == 'backspace':
            self.current_box = self.last_box
            self.input_boxes[self.current_box].text = '*'
            self.last_box = self.current_box - 1
            return True
        if keycode[1] not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            return True
        if not self.current_box:
            self.current_box = 0
        self.input_boxes[self.current_box].text = keycode[1]
        self.last_box = self.current_box
        self.current_box += 1
        if self.current_box > len(self.input_boxes) - 1:
            self.focus = False
            self.current_box = None
            self.last_box = None

    def on_current_box(self, instance, value):
        if not value:
            return
        #from main import Hnnnng
        #self.input_boxes[value].md_bg_color = Hnnnng.get_running_app().theme_cls.accent_dark
        #self.input_boxes[self.last_box].md_bg_color = (0, 0, 0, 1)

    def on_touch_down(self, touch):
        super(NumberInput, self).on_touch_down(touch)
        return True
