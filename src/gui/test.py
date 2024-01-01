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
from src._loader import TemplateDetails
from src.gui._state import GlobalAccess
from src.gui.utils import HoverButton


class TestApp(BoxLayout, GlobalAccess):
    """Template Tester."""
    Builder.load_file(os.path.join(PATH.SRC_DATA_KV, "test.kv"))

    def on_load(self, *args) -> None:
        """Add selector and toggle buttons."""
        self.selector = TemplateSelector(
            self, size_hint=(.8, .8))
        self.main.toggle_buttons.extend([
            self.ids.test_all,
            self.ids.test_target,
            self.ids.test_all_deep
        ])

    def select_template(self):
        """Select a target template to test."""
        self.selector.open()


class TemplateSelector(Popup, GlobalAccess):
    """Popup selector for selecting a template to call 'Test Target' on."""

    def __init__(self, root: TestApp, **kwargs):
        self.test_app = root
        super().__init__(**kwargs)

    def on_load(self, *args) -> None:
        """Add template buttons to template selector."""
        for card_type, templates in {
            t: temps for cat, cat_map in
            self.main.template_map.items() for
            t, temps in cat_map['map'].items()
        }.items():

            # Add title label
            self.ids.content.add_widget(
                Label(
                    text=card_type.replace("_", " ").title(),
                    size_hint=(1, None),
                    font_size=sp(25),
                    height=dp(45)))

            # Add buttons
            [self.ids.content.add_widget(SelectorButton(
                self.test_app,
                template=template,
                card_type=card_type,
                text=template['name']
            )) for name, template in templates.items()]


class SelectorButton(HoverButton, GlobalAccess):
    """Button which calls 'Test Target' on a given template."""

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
        self.test_app.selector.dismiss()
