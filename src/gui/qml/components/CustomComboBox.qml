pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls

ComboBox {
    id: control

    required property SystemPalette systemPalette
    property var itemTextColor
    property color _selectedTextColor: itemTextColor ? itemTextColor(control.currentIndex) : systemPalette.buttonText
    property var tooltipModel: undefined

    background.implicitHeight: 30
    palette.buttonText: _selectedTextColor
    delegate: CustomMenuItem {
        id: controlDelegate

        required property var model
        required property int index

        systemPalette: control.systemPalette

        palette.windowText: control.itemTextColor ? control.itemTextColor(index) : systemPalette.windowText
        width: ListView.view.width
        text: model[control.textRole]
        font.weight: control.currentIndex === index ? Font.DemiBold : Font.Normal
        highlighted: control.highlightedIndex === index
        hoverEnabled: control.hoverEnabled

        ToolTip {
            parent: controlDelegate
            visible: controlDelegate.hovered && Boolean(control.tooltipModel)
            delay: 50
            text: control.tooltipModel ? control.tooltipModel[controlDelegate.index] : ""
        }
    }

    Component.onCompleted: {
        indicator.color = systemPalette.text;
    }
}
