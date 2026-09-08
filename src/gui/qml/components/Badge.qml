pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Layouts

Rectangle {
    id: badge

    required property string text
    required property color textColor
    required property color bgColor
    property double fontSize: 8
    property bool hovered: hoverHandler.hovered

    implicitWidth: layout.implicitWidth + 15
    implicitHeight: layout.implicitHeight + 5
    radius: 10
    color: bgColor

    RowLayout {
        id: layout

        anchors.centerIn: parent

        Text {
            Layout.fillWidth: true

            text: badge.text
            font.pointSize: badge.fontSize
            color: badge.textColor
        }
    }

    HoverHandler {
        id: hoverHandler
    }
}
