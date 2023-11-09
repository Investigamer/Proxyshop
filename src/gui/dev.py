"""
DEV MODE
"""
# Standard Library Imports
import os
import threading

# Third Party Imports
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label

# Local Imports
from src.constants import con
from src.loader import get_templates, TemplateDetails
from src.gui.utils import HoverButton


class TestApp(BoxLayout):
    """
    Template Tester
    """
    Builder.load_file(os.path.join(con.path_kv, "dev.kv"))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selector = None

    def select_template(self):
        self.selector = TemplateSelector(self)
        self.selector.open()

    def test_target(self, card_type: str, template: TemplateDetails):
        self.selector.dismiss()
        threading.Thread(
            target=App.get_running_app().test_target,
            args=(card_type, template), daemon=True
        ).start()


class TemplateSelector(Popup):
    def __init__(self, test_app: TestApp, **kwargs):
        self.test_app = test_app
        self.size_hint = (.8, .8)
        super().__init__(**kwargs)

        # Add template buttons
        for card_type, templates in get_templates().items():
            self.ids.content.add_widget(Label(
                text=card_type.replace("_", " ").title(),
                size_hint=(1, None),
                font_size=25,
                height=45
            ))
            for template in templates:
                self.ids.content.add_widget(SelectorButton(
                    self.test_app,
                    template=template,
                    card_type=card_type,
                    text=template['name']
                ))


class SelectorButton(HoverButton):
    def __init__(self, root: TestApp, template: TemplateDetails, card_type: str, **kwargs):
        super().__init__(**kwargs)
        self.test_app = root
        self.card_type = card_type
        self.template = template
        self.size_hint = (1, None)
        self.font_size = 20
        self.height = 35

    def on_release(self, **kwargs):
        self.test_app.test_target(self.card_type, self.template)
