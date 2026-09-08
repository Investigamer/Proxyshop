pragma ComponentBehavior: Bound
import QtCore
import QtQml
import QtQuick
import QtQuick.Controls
import QtQuick.Dialogs
import QtQuick.Layouts

import qml.components
import qml.dialogs

ApplicationWindow {
    id: pluginUpdaterWindow

    required property SystemPalette systemPalette
    required property string emojiFontName
    required property var updaterModel
    required property var pathModel

    SortFilterProxyModel {
        id: sfProxyModel
        model: pluginUpdaterWindow.updaterModel
        sorters: [
            StringSorter {
                roleName: "name"
            }
        ]
    }

    function getVisualModelIndex(idx: int): int {
        return sfProxyModel.mapFromSource(updaterModel.index(idx, 0)).row;
    }

    title: "Plugin manager"
    width: 800
    height: 640
    visible: true
    color: systemPalette.window

    Settings {
        id: settings

        category: "PluginUpdater"
        location: pluginUpdaterWindow.pathModel.get_preferences_path("PluginUpdater.ini")

        property alias windowWidth: pluginUpdaterWindow.width
        property alias windowHeight: pluginUpdaterWindow.height
        property alias windowX: pluginUpdaterWindow.x
        property alias windowY: pluginUpdaterWindow.y

        property var updaterSplitState
    }

    Component.onCompleted: {
        updaterSplit.restoreState(settings.updaterSplitState);
        if (updaterModel.rowCount() < 1 && !updaterModel.fetching_data)
            updaterModel.fetch_data();
    }
    Component.onDestruction: {
        settings.updaterSplitState = updaterSplit.saveState();
    }

    MessageDialog {
        id: messageDialog

        title: "Uninstall plugin"
        buttons: MessageDialog.Ok | MessageDialog.Cancel
        modality: Qt.NonModal
        popupType: Popup.Window
    }

    CustomTextInputDialog {
        id: textInputDialog

        anchors.centerIn: Overlay.overlay

        systemPalette: pluginUpdaterWindow.systemPalette
        dialogTitle: "Add Plugin"
        dialogText: "Enter a URL to a Git repository, which contains a Proxyshop compatible plugin.<br>E.g. <i>https://github.com/author/plugin-name.git</i>"
        placeholderText: "https://github.com/<author>/<name>.git"

        onTextAccepted: function (text: string): void {
            pluginUpdaterWindow.updaterModel.add_plugin(text);
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        Rectangle {
            Layout.fillWidth: true

            implicitHeight: headerContent.implicitHeight
            color: pluginUpdaterWindow.systemPalette.button

            RowLayout {
                id: headerContent

                anchors.right: parent.right
                spacing: 10

                CustomButton {
                    systemPalette: pluginUpdaterWindow.systemPalette
                    text: `<font face="${pluginUpdaterWindow.emojiFontName}">➕</font> Add Plugin`
                    onClicked: textInputDialog.open()
                }
            }
        }

        SplitView {
            id: updaterSplit

            Layout.fillWidth: true
            Layout.fillHeight: true

            orientation: Qt.Horizontal

            Loader {
                id: listLoader

                SplitView.fillHeight: true
                SplitView.fillWidth: true

                asynchronous: true
                sourceComponent: pluginUpdaterWindow.updaterModel.fetching_data ? fetchingIndicatorComponent : availablePluginsListComponent

                Component {
                    id: fetchingIndicatorComponent

                    Item {
                        BusyIndicator {
                            id: indicator

                            anchors.centerIn: parent
                            implicitWidth: 50
                            implicitHeight: 50
                            running: pluginUpdaterWindow.updaterModel.fetching_data

                            palette.dark: pluginUpdaterWindow.systemPalette.text
                        }
                    }
                }
                Component {
                    id: availablePluginsListComponent

                    ListView {
                        id: availablePluginsList

                        property alias pluginsList: availablePluginsList

                        orientation: ListView.Vertical
                        boundsBehavior: Flickable.StopAtBounds
                        boundsMovement: Flickable.StopAtBounds
                        reuseItems: true
                        clip: true
                        focus: true
                        highlight: Rectangle {
                            height: availablePluginsList.currentItem?.height ?? 0
                            width: availablePluginsList.currentItem?.width ?? 0
                            color: pluginUpdaterWindow.systemPalette.highlight
                            y: availablePluginsList.currentItem?.y ?? 0
                        }
                        highlightFollowsCurrentItem: false
                        currentIndex: pluginUpdaterWindow.getVisualModelIndex(pluginUpdaterWindow.updaterModel.selected_index)
                        model: sfProxyModel
                        delegate: CustomItemDelegate {
                            id: availablePluginsListDelegate

                            required property int index
                            required property string id
                            required property string name
                            required property string author
                            required property string url
                            required property string installed_version
                            required property string available_version
                            required property string path
                            required property bool downloading
                            required property bool is_user_defined
                            readonly property int sourceIndex: sfProxyModel.mapToSource(sfProxyModel.index(index, 0)).row

                            property bool canDownload: !installed_version && available_version
                            property bool hasUpdateAvailable: available_version && installed_version && (installed_version !== available_version)

                            systemPalette: pluginUpdaterWindow.systemPalette
                            width: availablePluginsList.width
                            height: 30
                            highlighted: false

                            onClicked: {
                                pluginUpdaterWindow.updaterModel.selected_index = sourceIndex;
                            }

                            contentItem: RowLayout {
                                anchors.fill: parent
                                anchors.leftMargin: 10
                                spacing: 10

                                Text {
                                    Layout.alignment: Qt.AlignLeft

                                    text: availablePluginsListDelegate.name
                                    color: availablePluginsListDelegate.installed_version ? (pluginUpdaterWindow.updaterModel.selected_index === availablePluginsListDelegate.sourceIndex ? pluginUpdaterWindow.systemPalette.highlightedText : pluginUpdaterWindow.systemPalette.text) : pluginUpdaterWindow.systemPalette.placeholderText
                                }
                                Item {
                                    Layout.fillWidth: true
                                }
                                Loader {
                                    Layout.alignment: Qt.AlignRight

                                    asynchronous: true
                                    sourceComponent: availablePluginsListDelegate.is_user_defined ? removeButtonComponent : undefined

                                    Component {
                                        id: removeButtonComponent

                                        CustomButton {
                                            systemPalette: pluginUpdaterWindow.systemPalette
                                            text: "Remove"
                                            enabled: !availablePluginsListDelegate.downloading
                                            onClicked: {
                                                function onAccepted() {
                                                    messageDialog.accepted.disconnect(onAccepted);
                                                    messageDialog.rejected.disconnect(onRejected);
                                                    pluginUpdaterWindow.updaterModel.remove_added_plugin(availablePluginsListDelegate.sourceIndex);
                                                }

                                                function onRejected() {
                                                    messageDialog.accepted.disconnect(onAccepted);
                                                    messageDialog.rejected.disconnect(onRejected);
                                                }

                                                messageDialog.title = "Remove plugin";
                                                messageDialog.text = `Are you sure you want remove the <b>${availablePluginsListDelegate.name}</b> plugin from the list? If the plugin is installed, this will also delete the plugin's directory including templates and saved settings.`;
                                                messageDialog.accepted.connect(onAccepted);
                                                messageDialog.rejected.connect(onRejected);
                                                messageDialog.open();
                                            }
                                        }
                                    }
                                }
                                Loader {
                                    Layout.alignment: Qt.AlignRight

                                    asynchronous: true
                                    sourceComponent: availablePluginsListDelegate.installed_version ? uninstallButtonComponent : undefined

                                    Component {
                                        id: uninstallButtonComponent

                                        CustomButton {
                                            systemPalette: pluginUpdaterWindow.systemPalette
                                            text: "Uninstall"
                                            enabled: !availablePluginsListDelegate.downloading
                                            onClicked: {
                                                function onAccepted() {
                                                    messageDialog.accepted.disconnect(onAccepted);
                                                    messageDialog.rejected.disconnect(onRejected);
                                                    pluginUpdaterWindow.updaterModel.remove_plugin(availablePluginsListDelegate.sourceIndex);
                                                }

                                                function onRejected() {
                                                    messageDialog.accepted.disconnect(onAccepted);
                                                    messageDialog.rejected.disconnect(onRejected);
                                                }

                                                messageDialog.title = "Uninstall plugin";
                                                messageDialog.text = `Are you sure you want uninstall the <b>${availablePluginsListDelegate.name}</b> plugin? This will also delete the plugin's templates and saved settings.`;
                                                messageDialog.accepted.connect(onAccepted);
                                                messageDialog.rejected.connect(onRejected);
                                                messageDialog.open();
                                            }
                                        }
                                    }
                                }
                                CustomButton {
                                    id: downloadButton

                                    Layout.alignment: Qt.AlignRight

                                    systemPalette: pluginUpdaterWindow.systemPalette
                                    text: {
                                        if (availablePluginsListDelegate.downloading) {
                                            return "Downloading";
                                        }
                                        if (availablePluginsListDelegate.hasUpdateAvailable) {
                                            return "Update";
                                        }
                                        if (availablePluginsListDelegate.canDownload) {
                                            return "Download";
                                        }
                                        if (availablePluginsListDelegate.installed_version) {
                                            return "Installed";
                                        }
                                        return "Unavailable";
                                    }
                                    enabled: !availablePluginsListDelegate.downloading && (availablePluginsListDelegate.canDownload || availablePluginsListDelegate.hasUpdateAvailable)
                                    onClicked: {
                                        pluginUpdaterWindow.updaterModel.download_plugin(availablePluginsListDelegate.sourceIndex);
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

                property var selectedItem: listLoader.item?.pluginsList?.currentItem

                SplitView.fillHeight: true
                SplitView.preferredWidth: 200

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
                        const pluginPath = selectedUpdaterItemDetails.selectedItem ? pluginUpdaterWindow.pathModel.plugins_directory + "/" + selectedUpdaterItemDetails.selectedItem.id : "";
                        return [
                            {
                                name: "Name:",
                                isTitle: true
                            },
                            {
                                name: selectedUpdaterItemDetails.selectedItem?.name ?? "",
                                isTitle: false
                            },
                            {
                                name: "Author:",
                                isTitle: true
                            },
                            {
                                name: selectedUpdaterItemDetails.selectedItem?.author ?? "",
                                isTitle: false
                            },
                            {
                                name: "URL:",
                                isTitle: true
                            },
                            {
                                name: selectedUpdaterItemDetails.selectedItem?.url ? `<a href="${selectedUpdaterItemDetails.selectedItem.url}">${selectedUpdaterItemDetails.selectedItem.url}</a>` : "Not available",
                                isTitle: false,
                                wrap: Text.WrapAnywhere
                            },
                            {
                                name: "Installed version:",
                                isTitle: true
                            },
                            {
                                name: selectedUpdaterItemDetails.selectedItem?.installed_version || "Not installed",
                                isTitle: false,
                                wrap: Text.WrapAnywhere
                            },
                            {
                                name: "Available version:",
                                isTitle: true
                            },
                            {
                                name: selectedUpdaterItemDetails.selectedItem?.available_version || "Not available",
                                isTitle: false,
                                wrap: Text.WrapAnywhere
                            },
                            {
                                name: "Path:",
                                isTitle: true
                            },
                            {
                                name: selectedUpdaterItemDetails.selectedItem?.installed_version ? `<a href="${pluginPath}">${pluginPath}</a>` : "Not installed",
                                isTitle: false,
                                wrap: Text.WrapAnywhere
                            }
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
                        color: pluginUpdaterWindow.systemPalette.text
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
}
