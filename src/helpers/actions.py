"""
* Helpers: Actions
"""
# Third Party Imports
from photoshop.api import (
    DialogModes,
    ActionDescriptor,
    ActionReference
)

# Local Imports
from src import APP

# QOL Definitions
sID = APP.stringIDToTypeID
cID = APP.charIDToTypeID
NO_DIALOG = DialogModes.DisplayNoDialogs

"""
* Working With Actions
"""


def run_action(action_set: str, action: str) -> None:
    """Runs a Photoshop action.

    Args:
        action_set: Name of the group the action is in.
        action: Name of the action.
    """
    desc310 = ActionDescriptor()
    ref7 = ActionReference()
    desc310.putBoolean(sID("dontRecord"), False)
    desc310.putBoolean(sID("forceNotify"), True)
    ref7.putName(sID("action"),  action)
    ref7.putName(sID("actionSet"),  action_set)
    desc310.putReference(sID("target"),  ref7)
    APP.ExecuteAction(sID("play"), desc310, NO_DIALOG)
