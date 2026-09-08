pragma ComponentBehavior: Bound
import QtQml
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import qml.components

ApplicationWindow {
    id: imageTransformWindow

    required property SystemPalette systemPalette
    required property QtObject transformModel

    title: "Transform images"
    width: 300
    height: 360
    leftPadding: 10
    topPadding: 10
    rightPadding: 10
    bottomPadding: 10
    visible: true
    color: systemPalette.window

    ColumnLayout {
        anchors.fill: parent

        spacing: 10

        RowLayout {
            Layout.fillWidth: true

            Text {
                Layout.alignment: Qt.AlignLeft
                Layout.fillWidth: true

                text: "Format"
                color: imageTransformWindow.systemPalette.text
            }
            CustomComboBox {
                Layout.alignment: Qt.AlignRight

                systemPalette: imageTransformWindow.systemPalette
                model: imageTransformWindow.transformModel.image_file_formats
                currentValue: imageTransformWindow.transformModel.image_file_format

                onActivated: idx => {
                    imageTransformWindow.transformModel.image_file_format = imageTransformWindow.transformModel.image_file_formats[currentIndex];
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true

            Text {
                Layout.alignment: Qt.AlignLeft
                Layout.fillWidth: true

                text: "Downscale"
                color: imageTransformWindow.systemPalette.text
            }
            CustomCheckBox {
                Layout.alignment: Qt.AlignRight

                systemPalette: imageTransformWindow.systemPalette
                checked: imageTransformWindow.transformModel.downscale

                onClicked: {
                    imageTransformWindow.transformModel.downscale = !imageTransformWindow.transformModel.downscale;
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true

            Text {
                Layout.alignment: Qt.AlignLeft
                Layout.fillWidth: true

                text: "Target width (px)"
                color: imageTransformWindow.systemPalette.text
            }
            CustomSpinBox {
                Layout.alignment: Qt.AlignRight

                editable: true
                from: 1
                to: 100000
                value: imageTransformWindow.transformModel.downscale_width

                onValueModified: {
                    imageTransformWindow.transformModel.downscale_width = value;
                }
            }
        }

        Text {
            Layout.fillWidth: true

            text: `Typical widths for a proxy image, that has bleed, at different levels of DPI include:
600:  1632 px
800:  2176 px
1200: 3264 px`
            color: imageTransformWindow.systemPalette.text
            wrapMode: Text.WordWrap
        }

        RowLayout {
            Layout.fillWidth: true

            Text {
                Layout.alignment: Qt.AlignLeft
                Layout.fillWidth: true

                text: "Quality"
                color: imageTransformWindow.systemPalette.text
            }
            CustomSpinBox {
                Layout.alignment: Qt.AlignRight

                editable: true
                from: 1
                to: 100
                value: imageTransformWindow.transformModel.encoding_quality

                onValueModified: {
                    imageTransformWindow.transformModel.encoding_quality = value;
                }
            }
        }

        Text {
            Layout.fillWidth: true

            text: "Quality doesn't affect PNG encoding."
            color: imageTransformWindow.systemPalette.text
            wrapMode: Text.WordWrap
        }

        CustomButton {
            Layout.alignment: Qt.AlignRight

            systemPalette: imageTransformWindow.systemPalette
            bgColor: imageTransformWindow.systemPalette.button
            text: "Transform"
            onClicked: imageTransformWindow.transformModel.transform_images()
        }

        Item {
            Layout.fillHeight: true
        }
    }
}
