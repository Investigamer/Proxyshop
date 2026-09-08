pragma ComponentBehavior: Bound
import QtQml
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import qml.components

ListView {
    id: batchRenderList

    required property SystemPalette systemPalette
    required property AbstractListModel batchModel
    required property QtObject pathModel
    property double requiredLayoutNameWidth: 0

    TextMetrics {
        id: textMetrics
    }

    Component.onCompleted: {
        let requiredW = 0;
        for (const name of batchModel.layout_names()) {
            textMetrics.text = name;
            if (textMetrics.width > requiredW) {
                requiredW = textMetrics.width;
            }
        }
        textMetrics.destroy();
        requiredLayoutNameWidth = requiredW + 10;
    }

    spacing: 1
    orientation: ListView.Vertical
    boundsBehavior: Flickable.StopAtBounds
    boundsMovement: Flickable.StopAtBounds
    reuseItems: true
    clip: true
    focus: true
    highlightFollowsCurrentItem: false
    currentIndex: -1
    model: batchModel
    delegate: RowLayout {
        id: batchRenderListDelegate

        width: batchRenderList.width
        height: 30
        spacing: 0

        required property int index
        required property string name
        required property int selected
        required property list<string> options
        required property list<bool> options_installed
        required property list<string> options_preview_img_path

        Text {
            Layout.alignment: Qt.AlignLeft
            Layout.minimumWidth: batchRenderList.requiredLayoutNameWidth
            Layout.leftMargin: 10

            text: batchRenderListDelegate.name
            color: batchRenderList.systemPalette.text
        }
        CustomComboBox {
            id: templateComboBox

            Layout.alignment: Qt.AlignRight
            Layout.fillWidth: true

            function getItemTextColor(index: int): color {
                return batchRenderListDelegate.options_installed[index] ? systemPalette.text : systemPalette.placeholderText;
            }

            systemPalette: batchRenderList.systemPalette
            itemTextColor: getItemTextColor
            implicitHeight: 30
            model: batchRenderListDelegate.options
            tooltipModel: batchRenderListDelegate.options_preview_img_path.map(path => `<img width="250" height="340" src="${path || batchRenderList.pathModel.preview_img_fallback}">`)
            currentIndex: batchRenderListDelegate.selected

            onActivated: idx => {
                batchRenderList.batchModel.select_template_for_layout(batchRenderListDelegate.index, templateComboBox.currentIndex);
            }
        }
    }

    ScrollBar.vertical: ScrollBar {}
}
