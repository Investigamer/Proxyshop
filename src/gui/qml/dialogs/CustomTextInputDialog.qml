pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import qml.components

Dialog {
    id: customTextInputDialog

    required property SystemPalette systemPalette
    property string dialogTitle: ""
    property string dialogText: ""
    property string placeholderText: ""
    property string textValue: ""

    signal textAccepted(string text)

    title: dialogTitle
    modal: true

    onAccepted: {
        textAccepted(inputField.text.trim());
        customTextInputDialog.close();
    }

    onOpened: inputField.focus = true

    ColumnLayout {
        anchors.fill: parent
        spacing: 8

        SelectableText {
            color: customTextInputDialog.systemPalette.text
            text: customTextInputDialog.dialogText
            wrapMode: Text.WordWrap
        }

        TextField {
            id: inputField
            text: customTextInputDialog.textValue
            placeholderText: placeholderText
            Layout.fillWidth: true
            onTextChanged: {
                customTextInputDialog.textValue = inputField.text;
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 2

            Item {
                Layout.fillWidth: true
            }
            CustomButton {
                Layout.minimumWidth: 75

                systemPalette: customTextInputDialog.systemPalette
                bgColor: customTextInputDialog.systemPalette.button
                text: "Ok"
                onClicked: customTextInputDialog.accept()
            }
            CustomButton {
                Layout.minimumWidth: 75

                systemPalette: customTextInputDialog.systemPalette
                bgColor: customTextInputDialog.systemPalette.button
                text: "Cancel"
                onClicked: customTextInputDialog.reject()
            }
        }
    }
}
