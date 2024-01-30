"""
* GUI Tab: Main Rendering Tab
"""
# Standard Library Imports
import os
from pathlib import Path
from typing import Optional

# Kivy Imports
from kivy.lang import Builder
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button

# Local Imports
from src._loader import TemplateDetails, TemplateCategoryMap
from src._state import PATH
from src.enums.mtg import layout_map_category
from src.gui.popup.settings import SettingsPopup
from src.gui._state import GUI, GlobalAccess
from src.gui.utils import (
    DynamicTabPanel,
    DynamicTabItem,
    HoverButton)
from src.utils.files import remove_config_file
from src.utils.properties import auto_prop_cached

"""
* Template Modules
"""


class MainPanel(BoxLayout, GlobalAccess):
    """Main panel to the 'Render Cards' tab."""
    Builder.load_file(os.path.join(PATH.SRC_DATA_KV, "main.kv"))

    @auto_prop_cached
    def toggle_buttons(self) -> list[Button]:
        """Add render and settings buttons."""
        return [
            self.ids.rend_targ_btn,
            self.ids.rend_all_btn,
            self.ids.app_settings_btn
        ]


class TemplateModule(DynamicTabPanel, GlobalAccess):
    """Module that loads template tabs."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._tab_layout.padding = '0dp', '10dp', '0dp', '0dp'
        self.tabs = []

        # Create a scroll box with listed templates for each category
        for cat, _ in layout_map_category.items():

            # Get the template map for this category
            templates: TemplateCategoryMap = self.main.template_map[cat]

            # If less than 2 templates exist for this category, skip it
            if len(templates['names']) < 2:
                continue

            # Add a tab for this category
            tab = DynamicTabItem(text=cat)
            tab.content = self.get_template_container(
                category=cat,
                templates=templates)
            self.tabs.append(tab)

        # Only add tabs when all are generated
        [self.add_widget(t) for t in self.tabs]

    @staticmethod
    def get_template_container(
        category: str,
        templates: TemplateCategoryMap
    ) -> 'TemplateTabContainer':
        """Return a template container for containing the list view and preview image.

        Args:
            category: Template type category, e.g. Transform.
            templates: Mapping of types -> name -> template details.

        Returns:
            TemplateTabContainer object to add to the panel.
        """

        # Create a scroll box and container
        scroll_box = TemplateView()
        container = TemplateTabContainer()

        # Add template list to the scroll box
        TL = TemplateList(
            category=category,
            templates=templates,
            preview=container.ids.preview_image)
        scroll_box.add_widget(TL)
        GUI.template_list.setdefault(category, []).append(TL)

        # Add scroll box to the container and return it
        container.ids.template_view_container.add_widget(scroll_box)
        return container


class TemplateTabContainer(BoxLayout):
    """Container that holds template list within each tab."""


class TemplateView(ScrollView):
    """Scrollable viewport for template list."""


class TemplateList(BoxLayout, GlobalAccess):
    """Builds a list of templates from a certain template type."""

    def __init__(self, category: str, templates: type[TemplateCategoryMap], preview: Image, **kwargs):
        super().__init__(**kwargs)
        self.category = category
        self.preview = preview
        self.templates = templates
        self.types = list(templates['map'].keys())
        self.add_template_rows()

    def add_template_rows(self) -> None:
        """Add a row for each template in this list."""
        missing, found = [], []

        # Create a list of buttons
        for name in self.templates['names']:

            # Get details for each type
            templates: dict[str, Optional[type[TemplateDetails]]] = {
                t: self.templates['map'][t].get(name) for t in self.types}

            # Is template installed?
            if not all([n['object'].is_installed for _, n in templates.items() if n]):
                missing.append(templates)
                continue

            # Add installed template
            widget = TemplateRow(
                category=self.category,
                template_map=templates,
                preview=self.preview)
            self.add_widget(widget)
            found.append(widget)

        # Add the missing templates
        uninstalled = []
        for m in missing:
            row = TemplateRow(
                category=self.category,
                template_map=m,
                preview=self.preview)
            row.disabled = True
            self.add_widget(row)
            uninstalled.append(row)

        # Were no templates found at all?
        if not any([found, uninstalled]):
            return

        # Select the first 'found' template in this list, otherwise select the first uninstalled
        btn = (found if found else uninstalled)[0].ids.toggle_button
        btn.state = 'down'
        btn.dispatch('on_press')

    def reload_template_rows(self) -> None:
        """Remove existing rows and generate new ones using current template data."""
        self.clear_widgets()
        self.add_template_rows()


class TemplateRow(BoxLayout, GlobalAccess):
    """Row containing template selector and governing buttons."""

    def __init__(self, category: str, template_map: dict[str, type[TemplateDetails]], preview: Image, **kwargs):
        super().__init__(**kwargs)

        # Key attributes
        self.image: Image = preview
        self.template_map: dict[str, type[TemplateDetails]] = template_map
        self.types: list[str] = list(template_map.keys())
        self.category: str = category

        # Establish the name and previews
        name, config, previews = '', None, [PATH.SRC_IMG_NOTFOUND] * len(self.types)
        for i, t in enumerate(self.types):
            if obj := template_map.get(t, {}):
                if not obj:
                    continue

                # Set the name if still empty
                if not name:
                    name = obj.get('name', '')

                # Add the preview image for this type
                previews[i] = obj['object'].get_path_preview(
                    class_name=obj['class_name'], class_type=t
                ) if obj.get('object') else PATH.SRC_IMG_NOTFOUND

                # Set the chosen config object
                if not config:
                    config = obj['config']
                    config.gui_elements.append(self)

        # Set name, config, and previews
        self.config = config
        self.name = name or 'Unknown'
        self.preview: list[Path] = previews
        self.ids.toggle_button.text = self.name
        self.preview_face = 0

        # Check if config file is present
        self.default_settings_button_check()

        # Add to GUI Dict
        GUI.template_row.setdefault(category, {})[self.name] = self
        GUI.template_btn.setdefault(category, {})[self.name] = self.ids.toggle_button
        GUI.template_btn_cfg.setdefault(category, {})[self.name] = self.settings_button

    """
    * GUI Elements
    """

    @property
    def settings_button(self) -> Button:
        """Button: Click to load template specific settings."""
        return self.ids.settings_button

    @property
    def reset_button(self) -> Button:
        """Button: Click to reset template specific settings to default (global)."""
        return self.ids.reset_default_button

    """
    * Utility Methods
    """

    def default_settings_button_check(self) -> None:
        """Checks for a template's config file and enables/disables the reset settings button."""
        self.ids.reset_default_button.disabled = False if self.config.has_template_ini else True

    def toggle_preview_image(self) -> None:
        """Toggles the preview image on multi-side templates like Transform."""
        if len(self.preview) < 2:
            return
        new_face = 0 if self.preview_face == 1 else 1
        self.image.source = str(self.preview[new_face])
        self.preview_face = new_face

    def set_preview_image(self) -> None:
        """Sets the preview image in the parent container to the main preview face of this template."""
        self.image.manager = self
        self.image.source = str(self.preview[0])
        self.preview_face = 0


class TemplateSettingsButton(HoverButton, GlobalAccess):
    """Opens the settings panel for a given template."""

    async def open_settings(self) -> None:
        """Opens a settings panel to customize the settings of a specific template class."""
        obj = self.parent
        cfg_panel = SettingsPopup(obj.template_map[obj.types[0]])
        cfg_panel.open()
        for row in obj.config.gui_elements:
            row.default_settings_button_check()


class TemplateResetDefaultButton(HoverButton, GlobalAccess):
    """Deletes the ini config file for a given template (resets its settings to default)."""

    async def reset_default(self) -> None:
        """Removes the INI config file containing customized settings for a specific template class."""
        if remove_config_file(self.parent.config.template_path_ini):
            self.console.update(f"Reset template '{self.parent.name}' to global settings!")
        for row in self.parent.config.gui_elements:
            row.default_settings_button_check()
