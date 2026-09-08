import QtQuick
import QtQuick.Controls
import QtQuick.Controls.impl

TextField {
    id: control

    implicitHeight: 30
    leftPadding: 4
    rightPadding: 4
    background: Rectangle {
        implicitWidth: 0
        implicitHeight: control.implicitHeight
        color: control.palette.base

        // Custom active highlight
        border.color: control.activeFocus ? control.palette.highlight : "transparent"
        border.width: control.activeFocus ? 2 : 0
    }
}