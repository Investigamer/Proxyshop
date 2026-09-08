pragma ComponentBehavior: Bound
import QtCore
import QtQuick
import QtQuick.Dialogs

FileDialog {
    id: fileDialog

    required property QtObject dialogModel
    required property Settings settings
    property string dialogId: "custom_file_dialog_id__" + dialogModel.dialog_id

    modality: dialogModel.modality
    title: dialogModel.title
    fileMode: dialogModel.file_mode
    nameFilters: dialogModel.name_filters
    onAccepted: {
        const currFold = fileDialog.currentFolder.toString();
        if (!currFold.startsWith("data:")) {
            settings.setValue(dialogId, currFold);
        }
        dialogModel.on_accepted(fileDialog.selectedFiles);
    }
    onRejected: dialogModel.on_rejected()
    onCurrentFolderChanged: dialogModel.current_folder = fileDialog.currentFolder

    Connections {
        target: fileDialog.dialogModel

        function onSelectFiles(): void {
            const saved = fileDialog.settings.value(fileDialog.dialogId, undefined);
            if (saved) {
                fileDialog.currentFolder = saved;
            }
            fileDialog.open();
        }
    }
}
