"""
ACTION HELPERS
"""
# Standard Library Imports

# Third Party Imports
from photoshop.api import (
    DialogModes, ActionDescriptor, ActionReference
)


# Local Imports
from src.constants import con

# QOL Definitions
app = con.app
sID = app.stringIDToTypeID
cID = app.charIDToTypeID
NO_DIALOG = DialogModes.DisplayNoDialogs


def run_action(action_set: str, action: str) -> None:
    """
    Runs a Photoshop action.
    @param action_set: Name of the group the action is in.
    @param action: Name of the action.
    """
    desc310 = ActionDescriptor()
    ref7 = ActionReference()
    desc310.putBoolean(sID("dontRecord"), False)
    desc310.putBoolean(sID("forceNotify"), True)
    ref7.putName(sID("action"),  action)
    ref7.putName(sID("actionSet"),  action_set)
    desc310.putReference(sID("target"),  ref7)
    app.ExecuteAction(sID("play"), desc310, NO_DIALOG)