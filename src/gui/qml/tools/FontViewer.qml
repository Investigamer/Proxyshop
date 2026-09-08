pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls

ApplicationWindow {
    id: window

    width: 400
    height: 640
    color: palet.window

    SystemPalette {
        id: palet
    }

    ListView {
        anchors.fill: parent
        model: Qt.fontFamilies()

        delegate: Item {
            id: fontDelegate

            required property string modelData

            height: 30
            width: ListView.view.width
            Text {
                font.family: fontDelegate.modelData
                text: fontDelegate.modelData
                color: palet.text
            }
        }
    }
}
