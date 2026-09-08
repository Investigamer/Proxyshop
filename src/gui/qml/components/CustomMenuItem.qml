pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls

MenuItem {
    id: control

    required property SystemPalette systemPalette

    background: Rectangle {
        implicitHeight: 30

        color: control.highlighted ? control.systemPalette.light : "transparent"
        visible: control.down || control.highlighted
    }
}
