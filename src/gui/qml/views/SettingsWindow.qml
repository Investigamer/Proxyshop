pragma ComponentBehavior: Bound
import QtCore
import QtQml
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import qml.components

ApplicationWindow {
    id: settingsWindow

    required property SystemPalette systemPalette
    required property QtObject pathModel
    required property string emojiFontName
    required property QtObject settingsTreeModel
    required property QtObject settingsModel

    title: "Settings"
    width: 800
    height: 640
    visible: true
    color: systemPalette.window

    component RoleData: QtObject {
        property string type
        property string title
    }

    SortFilterProxyModel {
        id: sfSettingsModel

        model: settingsWindow.settingsModel
        filters: [
            FunctionFilter {
                id: settingsFilter

                property string searchString: ""
                property string effectiveSearchString: searchString.toLowerCase()

                function filter(data: RoleData): bool {
                    if (!settingsFilter.searchString)
                        return true;
                    return data.type !== "title" && data.title.toLowerCase().includes(settingsFilter.effectiveSearchString);
                }
            }
        ]
    }

    Timer {
        id: settingsFilterInvalidationDebounce

        interval: 150
        repeat: false
        onTriggered: settingsFilter.invalidate()
    }

    Settings {
        id: settings

        category: "Settings"
        location: settingsWindow.pathModel.get_preferences_path("Settings.ini")

        property alias windowWidth: settingsWindow.width
        property alias windowHeight: settingsWindow.height
        property alias windowX: settingsWindow.x
        property alias windowY: settingsWindow.y
        property var settingsSectionsSplitState
    }

    Component.onCompleted: {
        settingsSectionsSplit.restoreState(settings.settingsSectionsSplitState);
    }
    Component.onDestruction: {
        settings.settingsSectionsSplitState = settingsSectionsSplit.saveState();
    }

    SplitView {
        id: settingsSectionsSplit

        anchors.fill: parent
        orientation: Qt.Horizontal

        TreeView {
            id: settingsSections

            SplitView.fillHeight: true
            SplitView.preferredWidth: 200
            SplitView.minimumWidth: 150

            boundsBehavior: Flickable.StopAtBounds
            boundsMovement: Flickable.StopAtBounds
            reuseItems: true
            clip: true
            focus: true
            animate: false
            alternatingRows: false
            palette.base: settingsWindow.systemPalette.window
            model: settingsWindow.settingsTreeModel
            delegate: TreeViewDelegate {
                id: settingsSectionDelegate

                required property string id
                required property string name
                required property bool has_config

                implicitWidth: settingsSections.width
                selected: settingsSections.rowAtIndex(settingsWindow.settingsTreeModel.selected_model_index) === row
                onClicked: {
                    settingsWindow.settingsTreeModel.selected_model_index = settingsSections.index(row, 0);
                }
                background.implicitHeight: 0
                background.implicitWidth: 0
                indicator.implicitHeight: 20

                // We have to override content item because otherwise it tries to get
                // display role in a way that for some reason doesn't reach the Python data model?
                contentItem: Label {
                    clip: false
                    text: settingsSectionDelegate.name
                    elide: Text.ElideRight
                    color: settingsSectionDelegate.has_config ? settingsSectionDelegate.highlighted ? settingsSectionDelegate.palette.highlightedText : settingsSectionDelegate.palette.buttonText : settingsWindow.systemPalette.placeholderText
                    visible: !settingsSectionDelegate.editing
                }
            }

            Connections {
                id: treeViewConnections

                target: settingsWindow.settingsTreeModel

                function onSelectedModelIndexChanged(): void {
                    const idx = settingsWindow.settingsTreeModel.selected_model_index;
                    if (idx.valid) {
                        settingsSections.expandToIndex(idx);
                        settingsSections.positionViewAtIndex(idx, TreeView.AlignCenter, Qt.point(0, 0), Qt.rect(0, 0, 0, 0));
                    }
                }
            }

            Timer {
                id: positionTimer

                interval: 50
                running: false
                repeat: true
                onTriggered: {
                    // Somewhat hacky way to wait for the model to load.
                    // This might not guarantee the model to be ready?
                    if (settingsWindow.settingsTreeModel.rowCount()) {
                        treeViewConnections.onSelectedModelIndexChanged();
                        running = false;
                    }
                }
            }

            Component.onCompleted: positionTimer.running = true
        }
        ColumnLayout {
            SplitView.fillHeight: true
            SplitView.fillWidth: true

            spacing: 0

            Rectangle {
                id: headerBackground

                Layout.alignment: Qt.AlignTop
                Layout.fillWidth: true
                Layout.minimumHeight: headerTitle.height + 10

                color: settingsWindow.systemPalette.button

                RowLayout {
                    id: settingsHeader

                    anchors.fill: parent
                    spacing: 5

                    SelectableText {
                        id: headerTitle

                        Layout.alignment: Qt.AlignLeft
                        Layout.leftMargin: 10

                        text: settingsWindow.settingsTreeModel.selected_title
                        font.pointSize: 16
                        color: settingsWindow.systemPalette.text
                    }
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.minimumHeight: settingsSearchInput.height
                        Layout.maximumHeight: settingsSearchInput.height

                        color: settingsWindow.systemPalette.base

                        RowLayout {
                            anchors.fill: parent
                            spacing: 3

                            Text {
                                Layout.leftMargin: 3

                                text: `<font face="${settingsWindow.emojiFontName}">🔍</font>`
                                font.pointSize: 11
                            }
                            CustomTextField {
                                id: settingsSearchInput

                                Layout.fillWidth: true

                                text: settingsFilter.searchString
                                color: settingsWindow.systemPalette.text
                                placeholderText: "Search settings"

                                function onSetValue() {
                                    settingsFilter.searchString = settingsSearchInput.text;
                                    settingsFilterInvalidationDebounce.restart();
                                }

                                //onEditingFinished: onSetValue()
                                onTextEdited: onSetValue()
                            }
                        }
                    }
                    CustomButton {
                        id: resetButton

                        systemPalette: settingsWindow.systemPalette
                        text: `<font face="${settingsWindow.emojiFontName}">🔄</font> Reset`
                        visible: settingsWindow.settingsModel.valid

                        ToolTip.delay: 300
                        ToolTip.visible: resetButton.hovered
                        ToolTip.text: "Restore default settings values"

                        onClicked: {
                            settingsWindow.settingsModel.reset();
                        }
                    }
                    CustomButton {
                        id: clearButton

                        Layout.rightMargin: 5

                        systemPalette: settingsWindow.systemPalette
                        text: `<font face="${settingsWindow.emojiFontName}">🧹</font> Clear`
                        visible: settingsWindow.settingsModel.valid

                        ToolTip.delay: 300
                        ToolTip.visible: clearButton.hovered
                        ToolTip.text: "Delete the settings file"

                        onClicked: {
                            settingsWindow.settingsModel.clear();
                        }
                    }
                }
            }
            ListView {
                id: settingsList

                Layout.fillHeight: true
                Layout.fillWidth: true

                orientation: ListView.Vertical
                boundsBehavior: Flickable.StopAtBounds
                boundsMovement: Flickable.StopAtBounds
                reuseItems: false
                clip: true
                spacing: 5
                highlightFollowsCurrentItem: false
                model: sfSettingsModel
                delegate: ItemDelegate {
                    id: settingsListDelegate

                    required property int index
                    required property string type
                    required property string title
                    // Beware: Typing desc as a string here converts undefined to "undefined" string
                    required property var desc
                    required property var value
                    required property var default_value
                    required property var options
                    property bool isTitle: settingsListDelegate.type === "title"
                    readonly property int sourceIndex: sfSettingsModel.mapToSource(sfSettingsModel.index(index, 0)).row

                    width: settingsList.width
                    highlighted: false
                    background: Rectangle {
                        color: settingsListDelegate.isTitle ? settingsWindow.systemPalette.base : "transparent"
                    }

                    contentItem: RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: 10
                        anchors.rightMargin: 10
                        spacing: 10

                        ColumnLayout {
                            Layout.alignment: settingsListDelegate.isTitle ? Qt.AlignVCenter : Qt.AlignTop
                            Layout.fillWidth: true

                            SelectableText {
                                Layout.alignment: settingsListDelegate.isTitle ? Qt.AlignVCenter : Qt.AlignTop
                                Layout.fillWidth: true

                                text: settingsListDelegate.isTitle ? settingsListDelegate.title : `<b>${settingsListDelegate.title}</b>`
                                color: settingsWindow.systemPalette.text
                                font.pointSize: settingsListDelegate.isTitle ? 12 : descText.font.pointSize
                            }
                            SelectableText {
                                id: descText

                                Layout.alignment: Qt.AlignTop
                                Layout.fillWidth: true

                                text: settingsListDelegate.desc ?? ""
                                color: settingsWindow.systemPalette.text
                                visible: Boolean(settingsListDelegate.desc)
                            }
                            SelectableText {
                                id: defaultText

                                Layout.alignment: Qt.AlignTop
                                Layout.fillWidth: true

                                text: "Default: " + settingsListDelegate.default_value
                                color: settingsWindow.systemPalette.placeholderText
                                visible: !settingsListDelegate.isTitle
                            }
                        }
                        Loader {
                            id: inputLoader

                            property bool isTextInput: sourceComponent === textInputComponent

                            Layout.alignment: Qt.AlignRight
                            Layout.minimumWidth: isTextInput ? 50 : 0
                            Layout.maximumWidth: isTextInput ? parent.width / 2 : inputLoader.implicitWidth

                            asynchronous: true
                            sourceComponent: {
                                switch (settingsListDelegate.type) {
                                case "bool":
                                    return checkboxComponent;
                                case "string":
                                    return textInputComponent;
                                case "numeric":
                                    if (Number.isInteger(settingsListDelegate.default_value)) {
                                        return spinBoxIntComponent;
                                    }
                                    return spinBoxDouble;
                                case "options":
                                    return comboBox;
                                case "int":
                                    return spinBoxIntComponent;
                                case "float":
                                    return spinBoxDouble;
                                default:
                                    return undefined;
                                }
                            }

                            Component {
                                id: textInputComponent

                                CustomTextField {
                                    id: settingTextInput

                                    text: settingsListDelegate.value
                                    color: settingsWindow.systemPalette.text

                                    function onSetValue() {
                                        settingsWindow.settingsModel.str_value_changed(settingsListDelegate.sourceIndex, settingTextInput.text);
                                    }

                                    onEditingFinished: onSetValue()

                                    Connections {
                                        target: settingsWindow

                                        function onClosing(): void {
                                            if (settingTextInput.activeFocus)
                                                settingTextInput.onSetValue();
                                        }
                                    }
                                }
                            }
                            Component {
                                id: checkboxComponent

                                CustomCheckBox {
                                    id: settingCheckbox

                                    systemPalette: settingsWindow.systemPalette
                                    checked: settingsListDelegate.value

                                    onClicked: settingsWindow.settingsModel.bool_value_changed(settingsListDelegate.sourceIndex, settingCheckbox.checked)
                                }
                            }
                            Component {
                                id: spinBoxIntComponent

                                CustomSpinBox {
                                    id: settingSpinBoxInt

                                    editable: true
                                    from: -2147483648
                                    to: 2147483647
                                    value: settingsListDelegate.value

                                    function onSetValue(): void {
                                        settingsWindow.settingsModel.int_value_changed(settingsListDelegate.sourceIndex, settingSpinBoxInt.value);
                                    }

                                    onValueModified: onSetValue()

                                    Connections {
                                        target: settingsWindow

                                        function onClosing(): void {
                                            if (settingSpinBoxInt.activeFocus) {
                                                // Forcibly trigger onValueModified on window close
                                                settingSpinBoxInt.focus = false;
                                                settingSpinBoxInt.focus = true;
                                            }
                                        }
                                    }
                                }
                            }
                            Component {
                                id: spinBoxDouble

                                CustomSpinBox {
                                    id: settingSpinBoxDouble

                                    editable: true
                                    from: -2147483648
                                    to: 2147483647
                                    value: decimalToInt(settingsListDelegate.value)
                                    stepSize: decimalFactor
                                    anchors.centerIn: parent

                                    property int decimals: 3
                                    property real realValue: value / decimalFactor
                                    readonly property int decimalFactor: Math.pow(10, decimals)

                                    function decimalToInt(decimal: double): int {
                                        return decimal * decimalFactor;
                                    }

                                    validator: RegularExpressionValidator {
                                        regularExpression: /[0-9]+[.]?[0-9]*/
                                    }

                                    // locale is of type Locale but throws a warning if annotated
                                    // citing insufficient annotation of the function
                                    textFromValue: function (value: double, locale): string {
                                        return (value / decimalFactor).toString();
                                    }

                                    valueFromText: function (text: string, locale): int {
                                        return Math.round(parseFloat(text) * decimalFactor);
                                    }

                                    function onSetValue(): void {
                                        settingsWindow.settingsModel.float_value_changed(settingsListDelegate.sourceIndex, settingSpinBoxDouble.realValue);
                                    }

                                    onValueModified: onSetValue()

                                    Connections {
                                        target: settingsWindow

                                        function onClosing(): void {
                                            if (settingSpinBoxDouble.activeFocus) {
                                                // Forcibly trigger onValueModified on window close
                                                settingSpinBoxDouble.focus = false;
                                                settingSpinBoxDouble.focus = true;
                                            }
                                        }
                                    }
                                }
                            }
                            Component {
                                id: comboBox

                                CustomComboBox {
                                    id: settingComboBox

                                    systemPalette: settingsWindow.systemPalette
                                    model: settingsListDelegate.options
                                    currentValue: settingsListDelegate.value

                                    onActivated: idx => {
                                        settingsWindow.settingsModel.str_value_changed(settingsListDelegate.sourceIndex, settingComboBox.model[idx]);
                                    }
                                }
                            }
                        }
                    }
                }

                ScrollBar.vertical: ScrollBar {}
            }
        }
    }
}
