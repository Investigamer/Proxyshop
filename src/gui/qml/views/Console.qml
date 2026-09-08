pragma ComponentBehavior: Bound
import QtCore
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import qml.components

ColumnLayout {
    id: root

    required property SystemPalette systemPalette
    required property AbstractListModel logModel
    required property QtObject pathModel
    required property string emojiFontFamily
    required property string monospaceFontFamily

    Settings {
        id: settings

        category: "Console"
        location: root.pathModel.get_preferences_path("Console.ini")

        property bool autoScroll: true
    }

    RowLayout {
        Layout.fillWidth: true

        Text {
            Layout.fillWidth: true
            Layout.leftMargin: 10
            Layout.topMargin: 5
            Layout.bottomMargin: 5

            text: "Log"
            color: root.systemPalette.text
        }
        CustomButton {
            Layout.alignment: Qt.AlignRight

            systemPalette: root.systemPalette
            text: `<font face="${root.emojiFontFamily}">⏬</font> Autoscroll`
            palette.buttonText: settings.autoScroll ? root.systemPalette.buttonText : root.systemPalette.placeholderText
            onClicked: settings.autoScroll = !settings.autoScroll
        }
        CustomButton {
            Layout.alignment: Qt.AlignRight

            systemPalette: root.systemPalette
            text: `<font face="${root.emojiFontFamily}">📋</font> Copy`
            onClicked: root.logModel.copy_log()
        }
    }
    ListView {
        id: logList

        Layout.fillHeight: true
        Layout.fillWidth: true

        leftMargin: 0
        rightMargin: 10
        orientation: ListView.Vertical
        boundsBehavior: Flickable.StopAtBounds
        boundsMovement: Flickable.StopAtBounds
        clip: true
        highlightFollowsCurrentItem: false
        model: root.logModel
        delegate: RowLayout {
            id: logDelegate

            required property int index
            required property string message
            required property int severity
            required property color color

            width: logList.width
            spacing: 0

            Rectangle {
                Layout.fillHeight: true

                implicitWidth: 5
                color: logDelegate.color
            }
            SelectableText {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.leftMargin: 5

                color: root.systemPalette.text
                text: logDelegate.message
                font.family: root.monospaceFontFamily
            }
        }

        onCountChanged: {
            if (settings.autoScroll)
                Qt.callLater(logList.positionViewAtEnd);
        }

        ScrollBar.vertical: ScrollBar {}
    }
}
