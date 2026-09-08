import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: window

    width: 800
    height: 300
    color: palet.window

    SystemPalette {
        id: palet
    }

    Flow {
        anchors.fill: parent
        spacing: 10

        ColumnLayout {
            Text {
                text: "accent"
                color: palet.text
            }
            Rectangle {
                width: 50
                height: 50
                color: palet.accent
            }
        }
        ColumnLayout {
            Text {
                text: "alternateBase"
                color: palet.text
            }
            Rectangle {
                width: 50
                height: 50
                color: palet.alternateBase
            }
        }
        ColumnLayout {
            Text {
                text: "base"
                color: palet.text
            }
            Rectangle {
                width: 50
                height: 50
                color: palet.base
            }
        }
        ColumnLayout {
            Text {
                text: "button"
                color: palet.text
            }
            Rectangle {
                width: 50
                height: 50
                color: palet.button
            }
        }
        ColumnLayout {
            Text {
                text: "buttonText"
                color: palet.text
            }
            Rectangle {
                width: 50
                height: 50
                color: palet.buttonText
            }
        }
        ColumnLayout {
            Text {
                text: "dark"
                color: palet.text
            }
            Rectangle {
                width: 50
                height: 50
                color: palet.dark
            }
        }
        ColumnLayout {
            Text {
                text: "highlight"
                color: palet.text
            }
            Rectangle {
                width: 50
                height: 50
                color: palet.highlight
            }
        }
        ColumnLayout {
            Text {
                text: "highlightedText"
                color: palet.text
            }
            Rectangle {
                width: 50
                height: 50
                color: palet.highlightedText
            }
        }
        ColumnLayout {
            Text {
                text: "light"
                color: palet.text
            }
            Rectangle {
                width: 50
                height: 50
                color: palet.light
            }
        }
        ColumnLayout {
            Text {
                text: "mid"
                color: palet.text
            }
            Rectangle {
                width: 50
                height: 50
                color: palet.mid
            }
        }
        ColumnLayout {
            Text {
                text: "midlight"
                color: palet.text
            }
            Rectangle {
                width: 50
                height: 50
                color: palet.midlight
            }
        }
        ColumnLayout {
            Text {
                text: "placeholderText"
                color: palet.text
            }
            Rectangle {
                width: 50
                height: 50
                color: palet.placeholderText
            }
        }
        ColumnLayout {
            Text {
                text: "shadow"
                color: palet.text
            }
            Rectangle {
                width: 50
                height: 50
                color: palet.shadow
            }
        }
        ColumnLayout {
            Text {
                text: "text"
                color: palet.text
            }
            Rectangle {
                width: 50
                height: 50
                color: palet.text
            }
        }
        ColumnLayout {
            Text {
                text: "window"
                color: palet.text
            }
            Rectangle {
                width: 50
                height: 50
                color: palet.window
            }
        }
        ColumnLayout {
            Text {
                text: "windowText"
                color: palet.text
            }
            Rectangle {
                width: 50
                height: 50
                color: palet.windowText
            }
        }
    }
}
