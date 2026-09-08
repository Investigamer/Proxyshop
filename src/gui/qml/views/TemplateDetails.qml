pragma ComponentBehavior: Bound
import QtCore
import QtQml
import QtQuick
import QtQuick.Controls

import qml.components

Rectangle {
    id: templateDetails

    required property SystemPalette systemPalette
    required property AbstractListModel templateListMdl
    required property QtObject pathModel
    property var img: getImage()
    property list<var> model: constructModel()

    function getImage(): var {
        const mdl = templateDetails.templateListMdl;
        return mdl.get_data(mdl.selected_index, "img") ?? pathModel.preview_img_fallback;
    }

    function constructModel(): list<var> {
        const idx = templateListMdl.selected_index;

        if (idx < -1 || templateListMdl.rowCount() < 1) {
            return [];
        }

        const plugin = templateListMdl.get_data(idx, "plugin");
        const installedTemplateFiles = templateListMdl.get_data(idx, "installed_template_files");
        const missingTemplateFiles = templateListMdl.get_data(idx, "missing_template_files");
        const isPlugin = Boolean(plugin);

        return [
            {
                name: "Name:",
                isTitle: true,
                isVisible: true
            },
            {
                name: templateListMdl.get_data(idx, "name") ?? "",
                isTitle: false,
                isVisible: true
            },
            {
                name: "Plugin:",
                isTitle: true,
                isVisible: isPlugin
            },
            {
                name: plugin ?? "",
                isTitle: false,
                isVisible: isPlugin
            },
            {
                name: "Supported layouts:",
                isTitle: true,
                isVisible: true
            },
            {
                name: templateListMdl.get_data(idx, "card_layouts").join(", "),
                isTitle: false,
                isVisible: true
            },
            {
                name: "Installed templates:",
                isTitle: true,
                isVisible: true
            },
            {
                name: installedTemplateFiles && installedTemplateFiles.length ? installedTemplateFiles.join(", ") : "None",
                isTitle: false,
                isVisible: true
            },
            {
                name: "Missing templates:",
                isTitle: true,
                isVisible: true
            },
            {
                name: missingTemplateFiles && missingTemplateFiles.length ? missingTemplateFiles.join(", ") : "None",
                isTitle: false,
                isVisible: true
            }
        ];
    }

    function updateSelectedItem() {
        templateDetails.img = getImage();
        templateDetails.model = constructModel();
    }

    Connections {
        target: templateDetails.templateListMdl

        function onSelectedIndexChanged() {
            templateDetails.updateSelectedItem();
        }

        function onModelReset() {
            templateDetails.updateSelectedItem();
        }

        function onDataChanged() {
            templateDetails.updateSelectedItem();
        }

        function onRowsRemoved() {
            templateDetails.updateSelectedItem();
        }
    }

    Settings {
        id: settings

        category: "TemplateDetails"
        location: templateDetails.pathModel.get_preferences_path("TemplateDetails.ini")

        property var detailsSplitState
    }

    Component.onCompleted: {
        detailsSplit.restoreState(settings.detailsSplitState);
    }
    Component.onDestruction: {
        settings.detailsSplitState = detailsSplit.saveState();
    }

    color: systemPalette.window

    SplitView {
        id: detailsSplit

        anchors.fill: parent
        orientation: Qt.Vertical

        Image {
            SplitView.fillWidth: true
            SplitView.preferredHeight: 270

            verticalAlignment: Image.AlignTop
            asynchronous: true
            source: templateDetails.img
            fillMode: Image.PreserveAspectFit
        }
        ListView {
            id: detailsTextFields

            SplitView.fillWidth: true
            SplitView.fillHeight: true

            spacing: 2
            orientation: ListView.Vertical
            boundsBehavior: Flickable.StopAtBounds
            boundsMovement: Flickable.StopAtBounds
            clip: true
            highlightFollowsCurrentItem: false
            currentIndex: -1
            model: templateDetails.model
            delegate: SelectableText {
                id: textFieldDelegate

                required property int index
                property var item: detailsTextFields.model[index]
                property string name: item.name
                property bool isTitle: item.isTitle
                property bool isVisible: item.isVisible

                leftPadding: 5
                rightPadding: 5
                width: detailsTextFields.width
                text: name
                color: templateDetails.systemPalette.text
                font.bold: isTitle
                visible: isVisible

                Component.onCompleted: {
                    if (!isVisible) {
                        textFieldDelegate.height = -detailsTextFields.spacing;
                    }
                }
            }

            ScrollBar.vertical: ScrollBar {}
        }
    }
}
