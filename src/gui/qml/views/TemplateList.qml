pragma ComponentBehavior: Bound
import QtQml
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQml.Models

import qml.components

ListView {
    id: templateList

    required property SystemPalette systemPalette
    required property AbstractListModel templateListMdl
    required property var openSettings

    SortFilterProxyModel {
        id: sfProxyModel
        model: templateList.templateListMdl
        sorters: [
            RoleSorter {
                roleName: "is_installed"
                sortOrder: Qt.DescendingOrder
            },
            StringSorter {
                roleName: "plugin"
            },
            StringSorter {
                roleName: "name"
            }
        ]
    }

    function getVisualModelIndex(idx: int): int {
        return sfProxyModel.mapFromSource(templateListMdl.index(idx, 0)).row;
    }

    function updateTemplateListSelection() {
        templateList.currentIndex = templateList.getVisualModelIndex(templateList.templateListMdl.selected_index);
    }

    Connections {
        target: sfProxyModel

        function onLayoutChanged() {
            templateList.updateTemplateListSelection();
        }
    }

    Connections {
        target: templateListMdl

        function onSelectedIndexChanged() {
            templateList.updateTemplateListSelection();
        }
    }

    Timer {
        id: initTimer
        interval: 50
        running: false
        repeat: false
        onTriggered: templateList.positionViewAtIndex(templateList.getVisualModelIndex(templateList.templateListMdl.selected_index), ListView.Center)
    }

    Component.onCompleted: {
        // Setting the view position in on completed doesn't work,
        // so as a workaround a small delay is used.
        // This might be because the delegates haven't been rendered at this point.
        initTimer.start();
    }

    orientation: ListView.Vertical
    boundsBehavior: Flickable.StopAtBounds
    boundsMovement: Flickable.StopAtBounds
    reuseItems: false
    clip: true
    focus: true
    highlight: Rectangle {
        height: templateList.currentItem?.height ?? 0
        width: templateList.currentItem?.width ?? 0
        color: templateList.systemPalette.highlight
        y: templateList.currentItem?.y ?? 0
    }
    highlightFollowsCurrentItem: false
    currentIndex: templateList.getVisualModelIndex(templateList.templateListMdl.selected_index)
    model: sfProxyModel
    delegate: CustomItemDelegate {
        id: templateListDelegate

        required property int index
        required property string name
        required property string plugin
        required property string plugin_id
        required property bool is_installed
        required property bool has_config
        required property list<string> card_layouts

        function getSourceIndex(): int {
            return sfProxyModel.mapToSource(sfProxyModel.index(index, 0)).row;
        }

        systemPalette: templateList.systemPalette
        width: templateList.width
        implicitHeight: 30
        highlighted: false

        onClicked: {
            templateList.templateListMdl.selected_index = getSourceIndex();
        }

        contentItem: RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 10
            anchors.rightMargin: 10
            spacing: 0

            Text {
                Layout.fillWidth: true
                Layout.rightMargin: 10

                text: templateListDelegate.name + (templateListDelegate.plugin ? ` (${templateListDelegate.plugin})` : "")
                color: templateListDelegate.is_installed ? templateList.systemPalette.text : templateList.systemPalette.placeholderText
            }
            Badge {
                id: layoutsBadge

                property int numVisibleLayoutNames: 3

                Layout.rightMargin: 10

                text: templateListDelegate.card_layouts.slice(0, numVisibleLayoutNames).join(", ") + (templateListDelegate.card_layouts.length > numVisibleLayoutNames ? ` +${templateListDelegate.card_layouts.length - numVisibleLayoutNames}` : "")
                textColor: templateList.systemPalette.text
                bgColor: templateList.systemPalette.alternateBase

                ToolTip.delay: 300
                ToolTip.visible: layoutsBadge.hovered
                ToolTip.text: templateListDelegate.card_layouts.join(", ")
            }
            CustomButton {
                systemPalette: templateList.systemPalette
                implicitWidth: 32
                text: "⚙️"
                onClicked: templateList.openSettings(templateListDelegate.name, undefined, templateListDelegate.plugin_id)
            }
            CustomButton {
                systemPalette: templateList.systemPalette
                implicitWidth: 32
                text: templateListDelegate.has_config ? "🧹" : ""
                onClicked: templateList.templateListMdl.clear_settings(templateListDelegate.getSourceIndex())
                enabled: templateListDelegate.has_config
            }
        }
    }

    ScrollBar.vertical: ScrollBar {}
}
