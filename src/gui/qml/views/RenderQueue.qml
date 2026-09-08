pragma ComponentBehavior: Bound
import QtCore
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import qml.components

ApplicationWindow {
    id: renderQueueWindow

    required property SystemPalette systemPalette
    required property string emojiFontName
    required property AbstractListModel queueModel
    required property QtObject pathModel

    title: "Render queue"
    width: 800
    height: 640
    visible: true
    color: systemPalette.window

    Settings {
        id: settings

        category: "RenderQueue"
        location: renderQueueWindow.pathModel.get_preferences_path("RenderQueue.ini")

        property alias windowWidth: renderQueueWindow.width
        property alias windowHeight: renderQueueWindow.height
        property alias windowX: renderQueueWindow.x
        property alias windowY: renderQueueWindow.y
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        Rectangle {
            Layout.fillWidth: true

            implicitWidth: headerContent.implicitWidth
            implicitHeight: headerContent.implicitHeight
            color: renderQueueWindow.systemPalette.button

            RowLayout {
                id: headerContent

                anchors.fill: parent
                spacing: 10

                Text {
                    Layout.alignment: Qt.AlignLeft
                    Layout.leftMargin: 10
                    Layout.topMargin: 5
                    Layout.bottomMargin: 5

                    text: "Currently rendering:"
                    font.pointSize: 12
                    color: renderQueueWindow.systemPalette.text
                }
                Loader {
                    Layout.alignment: Qt.AlignLeft
                    Layout.fillWidth: true
                    Layout.topMargin: 5
                    Layout.bottomMargin: 5

                    asynchronous: true
                    active: true
                    sourceComponent: renderQueueWindow.queueModel.is_rendering ? renderingActiveComponent : renderingInactiveComponent

                    Component {
                        id: renderingActiveComponent

                        RowLayout {
                            anchors.fill: parent

                            spacing: 5

                            ColumnLayout {
                                Layout.fillWidth: true

                                spacing: 2

                                SelectableText {
                                    text: renderQueueWindow.queueModel.rendering_image_name
                                    font.pointSize: 11
                                    color: renderQueueWindow.systemPalette.text

                                    ToolTip.delay: 300
                                    ToolTip.visible: renderingHoverHandler.hovered
                                    ToolTip.text: renderQueueWindow.queueModel.rendering_image_path

                                    HoverHandler {
                                        id: renderingHoverHandler
                                    }
                                }
                                Flow {
                                    Layout.fillWidth: true

                                    spacing: 2

                                    SelectableText {
                                        text: `<i>Card</i>: ${renderQueueWindow.queueModel.rendering_card_name} (${renderQueueWindow.queueModel.rendering_card_artist}) [${renderQueueWindow.queueModel.rendering_card_set}] {${renderQueueWindow.queueModel.rendering_card_collector_number}}`
                                        font.pointSize: 10
                                        color: renderQueueWindow.systemPalette.text
                                    }
                                    Item {
                                        implicitWidth: 13
                                        implicitHeight: 1
                                    }
                                    SelectableText {
                                        text: "<i>Layout</i>: " + renderQueueWindow.queueModel.rendering_layout_name
                                        font.pointSize: 10
                                        color: renderQueueWindow.systemPalette.text
                                    }
                                    Item {
                                        implicitWidth: 13
                                        implicitHeight: 1
                                    }
                                    SelectableText {
                                        text: "<i>Class name</i>: " + renderQueueWindow.queueModel.rendering_class_name
                                        font.pointSize: 10
                                        color: renderQueueWindow.systemPalette.text
                                    }
                                }
                            }
                            Item {
                                Layout.fillWidth: true
                            }
                            CustomButton {
                                Layout.alignment: Qt.AlignVCenter | Qt.AlignRight
                                Layout.rightMargin: 10

                                systemPalette: renderQueueWindow.systemPalette
                                text: "✕"
                                palette.buttonText: !enabled ? renderQueueWindow.systemPalette.placeholderText : hovered || down ? "red" : renderQueueWindow.systemPalette.buttonText
                                enabled: renderQueueWindow.queueModel.is_rendering

                                onClicked: renderQueueWindow.queueModel.cancel()
                            }
                        }
                    }
                    Component {
                        id: renderingInactiveComponent

                        SelectableText {
                            text: "Nothing"
                            font.pointSize: 11
                            color: renderQueueWindow.systemPalette.text
                        }
                    }
                }
            }
        }
        Rectangle {
            Layout.fillWidth: true

            implicitWidth: subheaderContent.implicitWidth
            implicitHeight: subheaderContent.implicitHeight
            color: renderQueueWindow.systemPalette.base

            RowLayout {
                id: subheaderContent

                anchors.fill: parent
                spacing: 5

                Text {
                    Layout.leftMargin: 10

                    text: "Queue"
                    color: renderQueueWindow.systemPalette.text
                }
                CustomButton {
                    Layout.alignment: Qt.AlignVCenter | Qt.AlignRight
                    Layout.rightMargin: 10

                    systemPalette: renderQueueWindow.systemPalette
                    text: `<font face="${renderQueueWindow.emojiFontName}">🧹</font> Clear`

                    onClicked: renderQueueWindow.queueModel.clear()
                }
            }
        }
        ListView {
            id: queueList

            property int indexZeroPadding: 0

            Connections {
                target: renderQueueWindow.queueModel

                function onRowsInserted() {
                    const requiredPadding = renderQueueWindow.queueModel.rowCount().toString().length;
                    if (requiredPadding != queueList.indexZeroPadding) {
                        queueList.indexZeroPadding = requiredPadding;
                    }
                }
                function onRowsRemoved() {
                    const requiredPadding = renderQueueWindow.queueModel.rowCount().toString().length;
                    if (requiredPadding != queueList.indexZeroPadding) {
                        queueList.indexZeroPadding = requiredPadding;
                    }
                }
            }

            TextMetrics {
                id: textMetrics
                text: "8888."
            }

            Layout.fillWidth: true
            Layout.fillHeight: true

            spacing: 5
            orientation: ListView.Vertical
            boundsBehavior: Flickable.StopAtBounds
            boundsMovement: Flickable.StopAtBounds
            clip: true
            focus: true
            highlightFollowsCurrentItem: false
            currentIndex: -1
            model: renderQueueWindow.queueModel
            delegate: RowLayout {
                id: queueDelegate

                required property int index
                required property string image_name
                required property string image_path
                required property string card_name
                required property string card_artist
                required property string card_set
                required property string card_collector_number
                required property string layout_name
                required property string class_name

                width: queueList.width
                spacing: 5

                SelectableText {
                    Layout.alignment: Qt.AlignTop
                    Layout.minimumWidth: textMetrics.width + 5
                    Layout.leftMargin: 10
                    Layout.topMargin: 2

                    text: queueDelegate.index.toString().padStart(queueList.indexZeroPadding, "0") + "."
                    font.pointSize: 11
                    color: renderQueueWindow.systemPalette.text
                }
                ColumnLayout {
                    Layout.alignment: Qt.AlignVCenter | Qt.AlignLeft
                    Layout.fillWidth: true
                    Layout.leftMargin: 10

                    spacing: 2

                    SelectableText {
                        Layout.alignment: Qt.AlignLeft

                        text: queueDelegate.image_name
                        font.pointSize: 10
                        color: renderQueueWindow.systemPalette.text

                        ToolTip.delay: 300
                        ToolTip.visible: hoverHandler.hovered
                        ToolTip.text: queueDelegate.image_path

                        HoverHandler {
                            id: hoverHandler
                        }
                    }
                    Flow {
                        Layout.alignment: Qt.AlignLeft
                        Layout.fillWidth: true

                        spacing: 2

                        SelectableText {
                            text: `<i>Card:</i> ${queueDelegate.card_name} (${queueDelegate.card_artist}) [${queueDelegate.card_set}] {${queueDelegate.card_collector_number}}`
                            font.pointSize: 9
                            color: renderQueueWindow.systemPalette.text
                        }
                        Item {
                            implicitWidth: 13
                            implicitHeight: 1
                        }
                        SelectableText {
                            text: "<i>Layout:</i> " + queueDelegate.layout_name
                            font.pointSize: 9
                            color: renderQueueWindow.systemPalette.text
                        }
                        Item {
                            implicitWidth: 13
                            implicitHeight: 1
                        }
                        SelectableText {
                            text: "<i>Class name:</i> " + queueDelegate.class_name
                            font.pointSize: 9
                            color: renderQueueWindow.systemPalette.text
                        }
                    }
                }
                Item {
                    Layout.fillWidth: true
                }
                CustomButton {
                    Layout.alignment: Qt.AlignTop | Qt.AlignRight
                    Layout.topMargin: 2
                    Layout.rightMargin: 10

                    systemPalette: renderQueueWindow.systemPalette
                    text: "✕"
                    palette.buttonText: hovered || down ? "red" : renderQueueWindow.systemPalette.buttonText

                    onClicked: renderQueueWindow.queueModel.dequeue(queueDelegate.index)
                }
            }

            ScrollBar.vertical: ScrollBar {}
        }
    }
}
