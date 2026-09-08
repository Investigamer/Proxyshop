pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls

Menu {
    id: control

    required property SystemPalette systemPalette

    delegate: CustomMenuItem {
        systemPalette: control.systemPalette
    }
    background: Rectangle {
        implicitWidth: 200
        implicitHeight: 40
        color: control.systemPalette.button
        border.color: control.systemPalette.mid
        border.width: 1
    }
}
