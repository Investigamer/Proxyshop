import QtQml
import QtQuick.Controls
import QtQuick.Dialogs

MessageDialog {
    id: customMessageDialog

    required property QtObject dialogContentModel

    title: dialogContentModel?.title ?? ""
    text: dialogContentModel?.text ?? ""
    informativeText: dialogContentModel?.informative_text ?? ""
    detailedText: dialogContentModel?.detailed_text ?? ""
    buttons: MessageDialog.Cancel | MessageDialog.Ok
    modality: Qt.NonModal
    popupType: Popup.Window

    onButtonClicked: function (button: int, role: int): void {
        switch (button) {
        case MessageDialog.Ok:
            dialogContentModel.ok();
            break;
        case MessageDialog.Cancel:
            dialogContentModel.cancel();
            break;
        }
    }

    Connections {
        target: customMessageDialog.dialogContentModel

        function onDismissed() {
            if (customMessageDialog.visible) {
                customMessageDialog.reject();
            }
        }
    }
}
