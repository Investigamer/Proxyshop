import QtQuick
import QtQuick.Controls

ItemDelegate {
    id: control

    required property SystemPalette systemPalette
    property color bgColor: "transparent"

    implicitHeight: 30
    padding: 0
    spacing: 0

    background: Rectangle {
        implicitHeight: 30
        implicitWidth: control.contentItem.implicitWidth
        color: control.highlighted ? control.systemPalette.highlight : control.bgColor

        Rectangle {
            anchors.fill: parent
            visible: control.enabled && (control.down || control.hovered)
            opacity: control.down ? 0.1 : 0.05
            color: control.systemPalette.text
        }
    }
}
