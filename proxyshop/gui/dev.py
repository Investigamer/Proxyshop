"""
DEV MODE
"""
import os
import threading

from kivy.app import App
from kivy.core.text import Label
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup

from proxyshop.core import get_templates
from proxyshop.gui.utils import HoverButton

cwd = os.getcwd()


class TestApp(BoxLayout):
    """
    Template Tester
    """
    Builder.load_file(os.path.join(cwd, "proxyshop/kivy/dev.kv"))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selector = None

    def select_template(self):
        self.selector = TemplateSelector(self)
        self.selector.open()

    def test_target(self, temp):
        self.selector.dismiss()
        threading.Thread(
            target=App.get_running_app().test_target,
            args=(temp[0], temp[1]), daemon=True
        ).start()


class TemplateSelector(Popup):
    def __init__(self, test_app, **kwargs):
        self.test_app = test_app
        self.size_hint = (.8, .8)
        super().__init__(**kwargs)

        # Add template buttons
        for k, v in get_templates().items():
            self.ids.content.add_widget(Label(
                text=k.replace("_", " ").title(),
                size_hint=(1, None),
                font_size=25,
                height=45
            ))
            for key, val in v.items():
                self.ids.content.add_widget(SelectorButton(
                    self.test_app,
                    [k, val],
                    text=key
                ))


class SelectorButton(HoverButton):
    def __init__(self, root, temp, **kwargs):
        super().__init__(**kwargs)
        self.test_app = root
        self.temp = temp
        self.size_hint = (1, None)
        self.font_size = 20
        self.height = 35

    def on_release(self, **kwargs):
        self.test_app.test_target(self.temp)
