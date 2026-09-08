import QtQuick
import QtQuick.Controls

TabButton {
    id: control

    required property SystemPalette systemPalette
    property color bgColor: "transparent"

    leftPadding: 8
    rightPadding: 8
    spacing: 0
    width: implicitWidth
    palette.brightText: systemPalette.placeholderText
    background: Rectangle {
        implicitHeight: 30
        implicitWidth: control.contentItem.implicitWidth
        color: control.bgColor

        Rectangle {
            anchors.fill: parent
            visible: control.enabled && (control.down || control.hovered)
            opacity: control.down ? 0.1 : 0.05
            color: control.systemPalette.text
        }
    }
}
