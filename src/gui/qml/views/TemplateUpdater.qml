pragma ComponentBehavior: Bound
import QtCore
import QtQml
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import qml.components

ApplicationWindow {
    id: templateUpdaterWindow

    required property SystemPalette systemPalette
    required property AbstractListModel updaterModel
    required property QtObject pathModel

    SortFilterProxyModel {
        id: sfProxyModel
        model: templateUpdaterWindow.updaterModel
        sorters: [
            StringSorter {
                roleName: "plugin"
            },
            StringSorter {
                roleName: "file_name"
            }
        ]
    }

    function getVisualModelIndex(idx: int): int {
        return sfProxyModel.mapFromSource(updaterModel.index(idx, 0)).row;
    }

    // From https://stackoverflow.com/a/20732091
    function humanFileSize(bytes: int): string {
        const i = bytes === 0 ? 0 : Math.floor(Math.log(bytes) / Math.log(1024));
        return `${(bytes / Math.pow(1024, i)).toFixed(2)} ${["B", "kB", "MB", "GB", "TB"][i]}`;
    }

    title: "Template updater"
    width: 800
    height: 640
    visible: true
    color: systemPalette.window

    Settings {
        id: settings

        category: "TemplateUpdater"
        location: templateUpdaterWindow.pathModel.get_preferences_path("TemplateUpdater.ini")

        property alias windowWidth: templateUpdaterWindow.width
        property alias windowHeight: templateUpdaterWindow.height
        property alias windowX: templateUpdaterWindow.x
        property alias windowY: templateUpdaterWindow.y

        property var updaterSplitState
    }

    Component.onCompleted: {
        updaterSplit.restoreState(settings.updaterSplitState);
        if (updaterModel.rowCount() < 1)
            updaterModel.fetch_data();
    }
    Component.onDestruction: {
        settings.updaterSplitState = updaterSplit.saveState();
    }

    SplitView {
        id: updaterSplit

        anchors.fill: parent
        orientation: Qt.Horizontal

        Loader {
            id: listLoader

            SplitView.fillHeight: true
            SplitView.fillWidth: true

            asynchronous: true
            sourceComponent: templateUpdaterWindow.updaterModel.fetching_data ? fetchingIndicatorComponent : availableTemplatesListComponent

            Component {
                id: fetchingIndicatorComponent

                Item {
                    BusyIndicator {
                        id: indicator

                        anchors.centerIn: parent
                        implicitWidth: 50
                        implicitHeight: 50
                        running: templateUpdaterWindow.updaterModel.fetching_data

                        palette.dark: templateUpdaterWindow.systemPalette.text
                    }
                }
            }
            Component {
                id: availableTemplatesListComponent

                ListView {
                    id: availableTemplatesList

                    property alias templatesList: availableTemplatesList

                    orientation: ListView.Vertical
                    boundsBehavior: Flickable.StopAtBounds
                    boundsMovement: Flickable.StopAtBounds
                    reuseItems: true
                    clip: true
                    focus: true
                    highlight: Rectangle {
                        height: availableTemplatesList.currentItem?.height ?? 0
                        width: availableTemplatesList.currentItem?.width ?? 0
                        color: templateUpdaterWindow.systemPalette.highlight
                        y: availableTemplatesList.currentItem?.y ?? 0
                    }
                    highlightFollowsCurrentItem: false
                    currentIndex: templateUpdaterWindow.getVisualModelIndex(templateUpdaterWindow.updaterModel.selected_index)
                    model: sfProxyModel
                    delegate: CustomItemDelegate {
                        id: availableTemplatesListDelegate

                        required property int index
                        required property string file_name
                        required property string google_drive_id
                        required property string img
                        required property string plugin
                        required property list<string> template_names
                        required property list<string> template_classes
                        required property list<string> layout_categories
                        required property string installed_version
                        required property string available_version
                        required property int download_size
                        required property bool downloading
                        readonly property int sourceIndex: sfProxyModel.mapToSource(sfProxyModel.index(index, 0)).row

                        property bool canDownload: !installed_version && available_version
                        property bool hasUpdateAvailable: available_version && installed_version && (installed_version !== available_version)

                        systemPalette: templateUpdaterWindow.systemPalette
                        width: availableTemplatesList.width
                        height: 30
                        highlighted: false

                        onClicked: {
                            templateUpdaterWindow.updaterModel.selected_index = sourceIndex;
                        }

                        contentItem: RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 10
                            spacing: 10

                            Text {
                                Layout.alignment: Qt.AlignLeft

                                text: availableTemplatesListDelegate.file_name + (availableTemplatesListDelegate.plugin ? ` (${availableTemplatesListDelegate.plugin})` : "")
                                color: availableTemplatesListDelegate.installed_version ? (templateUpdaterWindow.updaterModel.selected_index === availableTemplatesListDelegate.sourceIndex ? templateUpdaterWindow.systemPalette.highlightedText : templateUpdaterWindow.systemPalette.text) : templateUpdaterWindow.systemPalette.placeholderText
                            }
                            CustomButton {
                                id: downloadButton

                                Layout.alignment: Qt.AlignRight

                                systemPalette: templateUpdaterWindow.systemPalette
                                text: {
                                    if (availableTemplatesListDelegate.downloading) {
                                        return "Downloading";
                                    }
                                    if (availableTemplatesListDelegate.hasUpdateAvailable) {
                                        return "Update";
                                    }
                                    if (availableTemplatesListDelegate.canDownload) {
                                        return "Download";
                                    }
                                    if (availableTemplatesListDelegate.installed_version) {
                                        return "Installed";
                                    }
                                    return "Unavailable";
                                }
                                enabled: !availableTemplatesListDelegate.downloading && (availableTemplatesListDelegate.canDownload || availableTemplatesListDelegate.hasUpdateAvailable)
                                onClicked: {
                                    templateUpdaterWindow.updaterModel.download_template(availableTemplatesListDelegate.sourceIndex);
                                }
                            }
                        }
                    }

                    ScrollBar.vertical: ScrollBar {}
                }
            }
        }

        SplitView {
            id: selectedUpdaterItemDetails
            orientation: Qt.Vertical

            property var selectedItem: listLoader.item?.templatesList?.currentItem

            SplitView.fillHeight: true
            SplitView.preferredWidth: 200

            Image {
                SplitView.fillWidth: true
                SplitView.preferredHeight: 270

                verticalAlignment: Image.AlignTop
                asynchronous: true
                source: selectedUpdaterItemDetails.selectedItem?.img ?? templateUpdaterWindow.pathModel.preview_img_fallback
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
                model: {
                    return [
                        {
                            name: "File name:",
                            isTitle: true
                        },
                        {
                            name: selectedUpdaterItemDetails.selectedItem?.file_name ?? "",
                            isTitle: false
                        },
                        {
                            name: "Installed version:",
                            isTitle: true
                        },
                        {
                            name: selectedUpdaterItemDetails.selectedItem?.installed_version || "Not installed",
                            isTitle: false
                        },
                        {
                            name: "Available version:",
                            isTitle: true
                        },
                        {
                            name: selectedUpdaterItemDetails.selectedItem?.available_version || "Not available",
                            isTitle: false
                        },
                        {
                            name: "Download size:",
                            isTitle: true
                        },
                        {
                            name: templateUpdaterWindow.humanFileSize(selectedUpdaterItemDetails.selectedItem?.download_size ?? 0),
                            isTitle: false
                        },
                        {
                            name: "Template names:",
                            isTitle: true
                        },
                        {
                            name: selectedUpdaterItemDetails.selectedItem?.template_names.join(", ") ?? "",
                            isTitle: false
                        },
                        {
                            name: "Template layouts:",
                            isTitle: true
                        },
                        {
                            name: selectedUpdaterItemDetails.selectedItem?.layout_categories.join(", ") ?? "",
                            isTitle: false
                        },
                        {
                            name: "Template classes:",
                            isTitle: true
                        },
                        {
                            name: selectedUpdaterItemDetails.selectedItem?.template_classes.join(", ") ?? "",
                            isTitle: false
                        },
                    ];
                }
                delegate: SelectableText {
                    id: textFieldDelegate

                    required property int index
                    property var item: detailsTextFields.model[index]
                    property string name: item.name
                    property bool isTitle: item.isTitle
                    property bool isVisible: item.isVisible ?? true
                    property int wrap: item.wrapMode ?? Text.WordWrap

                    leftPadding: 5
                    rightPadding: 5
                    width: detailsTextFields.width
                    text: name
                    color: templateUpdaterWindow.systemPalette.text
                    font.bold: isTitle
                    visible: isVisible
                    wrapMode: wrap

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
}
