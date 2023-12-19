"""
* Test Mode App
"""
# Standard Library Imports
import os
import threading

# Third Party Imports
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.metrics import dp, sp

# Local Imports
from src._state import PATH
from src._loader import TemplateDetails, TemplateCategoryMap
from src.gui._state import GlobalAccess
from src.gui.utils import HoverButton


class TestApp(BoxLayout, GlobalAccess):
    """Template Tester."""
    #Builder.load_file(os.path.join(PATH.SRC_DATA_KV, "test.kv"))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selector = TemplateSelector(self)

    def select_template(self):
        """Select a target template to test."""
        self.selector.open()


class TemplateSelector(Popup, GlobalAccess):
    def __init__(self, root: TestApp, **kwargs):
        self.test_app = root
        super().__init__(
            size_hint=(.8, .8),
            **kwargs)

        # Templates by type
        template_map: TemplateCategoryMap = self.main.templates
        self.templates = {
            card_type: templates for category, mapped in template_map.items()
            for card_type, templates in mapped['map'].items()}

        # Add template buttons
        for card_type, templates in self.templates.items():
            self.ids.content.add_widget(Label(
                text=card_type.replace("_", " ").title(),
                size_hint=(1, None),
                font_size=sp(25),
                height=dp(45)
            ))
            for name, template in templates.items():
                self.ids.content.add_widget(SelectorButton(
                    self.test_app,
                    template=template,
                    card_type=card_type,
                    text=template['name']
                ))


class SelectorButton(HoverButton, GlobalAccess):
    def __init__(self, root: TestApp, template: TemplateDetails, card_type: str, **kwargs):
        super().__init__(**kwargs)
        self.test_app = root
        self.card_type = card_type
        self.template = template
        self.size_hint = (1, None)
        self.font_size = sp(20)
        self.height = dp(35)

    def on_release(self, **kwargs):
        """Launch app method 'test_target' on release."""
        threading.Thread(
            target=self.main.test_target,
            args=(self.card_type, self.template), daemon=True
        ).start()
