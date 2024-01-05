"""
* GUI Utility Behaviors
"""
# Third Party Imports
from kivy.app import App
from kivy.core.window import Window
from kivy.properties import BooleanProperty, ObjectProperty

"""
* Utility Classes
"""


class HoverBehavior(object):
    """Utility modifier class which adds hover behavior to layout elements.

    Events:
        `on_enter`: Fired when mouse enter the bbox of the widget.
        `on_leave`: Fired when the mouse exit the widget
    """
    hovered = BooleanProperty(False)
    border_point = ObjectProperty(None)

    def __init__(self, **kwargs):
        self.register_event_type('on_enter')
        self.register_event_type('on_leave')
        Window.bind(mouse_pos=self.on_mouse_pos)
        super(HoverBehavior, self).__init__(**kwargs)

    def on_mouse_pos(self, *args):
        if not self.get_root_window():
            return  # do proceed if I'm not displayed <=> If I have no parent
        pos = args[1]
        # Next line to_widget allowed to compensate for relative layout
        inside = self.collide_point(*self.to_widget(*pos))
        if self.hovered == inside:
            # We have already done what was needed
            return
        self.border_point = pos
        self.hovered = inside
        if inside:
            self.dispatch('on_enter')
        else:
            self.dispatch('on_leave')

    """
    BLANK METHODS - Overwritten by Extend Class, e.g. Button
    """

    def dispatch(self, action):
        return

    @staticmethod
    def collide_point(point: float):
        if point:
            return True
        return False

    @staticmethod
    def to_widget(point: list):
        return point

    @staticmethod
    def get_root_window():
        return App.root_window

    @staticmethod
    def register_event_type(event: str) -> None:
        return
