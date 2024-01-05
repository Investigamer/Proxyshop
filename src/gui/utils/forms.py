"""
* GUI Utility Form Elements
"""
# Third Party Imports
from kivy.uix.textinput import TextInput

"""
* Utility Input classes
"""


class InputItem(TextInput):
    """Track hint text in perpetuity, add QOL key binds."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.clicked = False
        self.original = self.text

    def _on_focus(self, instance, value, *args):
        """Preserve hint text."""
        if not self.clicked:
            self.clicked = True
            self.original = self.text
        super()._on_focus(instance, value, *args)

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        """Enable tab to next or previous input and F5 to reset."""
        if keycode[1] == 'tab':
            # Deal with tabbing between inputs
            if 'shift' in modifiers:
                nxt = self.get_focus_previous()
            else:
                nxt = self.get_focus_next()
            if nxt:
                self.focus = False
                nxt.focus = True
            return True
        if keycode[0] == 286:
            # F5 to reset text to hint text
            self.clicked = False
            self.text = self.original
        super().keyboard_on_key_down(window, keycode, text, modifiers)


class NoEnterInputItem(InputItem):
    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        """Disable next line."""
        if keycode[0] == 13:  # deal with cycle
            return False
        super().keyboard_on_key_down(window, keycode, text, modifiers)


class ValidatedInput(InputItem):
    """Limit text input based on numeric, length, and whitelisted terms."""
    def __init__(self, **kwargs):
        self._max_len = int(kwargs.pop('max_len', 0))
        self._whitelist = kwargs.pop('whitelist', [])
        self._numeric = bool(kwargs.pop('numeric', False))
        self._numeric_range = kwargs.pop('numeric_range', [0, 0])
        super().__init__(**kwargs)

    def insert_text(self, substring, from_undo=False) -> None:
        """
        3 character max, numeric with a small whitelist
        """
        # Character length requirement
        if self._max_len != 0 and len(self.text) > (self._max_len - 1):
            return

        # Numeric value or whitelisted value requirement
        if self._numeric and not (substring.isnumeric() or substring in self._whitelist):
            return

        # Numeric value in accepted range requirement
        if self._numeric and not (self._numeric_range[1] == 0 or (
            self._numeric_range[0] <= int(self.text + str(substring)) <= self._numeric_range[1]
        )):
            return

        # Value is validated
        return super().insert_text(substring, from_undo=from_undo)


class FourNumInput(ValidatedInput):
    """Utility definition, 4 numeric characters with whitelisted operators."""
    def __init__(self, **kwargs):
        super().__init__(max_len=4, numeric=True, whitelist=["*", "X", "Y", "+", "-"], **kwargs)


class ThreeNumInput(ValidatedInput):
    """Utility definition, 3 numeric characters with whitelisted operators."""
    def __init__(self, **kwargs):
        super().__init__(max_len=3, numeric=True, whitelist=["*", "X", "Y", "+", "-"], **kwargs)


class FourCharInput(ValidatedInput):
    """Utility definition, 4 of any kind of characters."""
    def __init__(self, **kwargs):
        super().__init__(max_len=4, **kwargs)


class Range100NumInput(ValidatedInput):
    """Utility definition, number between 1 and 100."""
    def __init__(self, **kwargs):
        super().__init__(numeric=True, numeric_range=[1, 100], **kwargs)
