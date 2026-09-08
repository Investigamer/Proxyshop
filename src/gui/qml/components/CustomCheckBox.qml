pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls

CheckBox {
    id: control

    required property SystemPalette systemPalette

    padding: 0
    spacing: 0
    implicitWidth: 25
    implicitHeight: 25
    indicator: Rectangle {
        anchors.fill: parent
        color: control.systemPalette.button

        Rectangle {
            anchors.fill: parent
            visible: control.enabled && (control.down || control.hovered)
            opacity: control.down ? 0.1 : 0.05
            color: control.systemPalette.text
        }
        Text {
            anchors.centerIn: parent
            text: "✔"
            font.pointSize: 11
            color: control.systemPalette.text
            visible: control.checked
        }
    }
}
