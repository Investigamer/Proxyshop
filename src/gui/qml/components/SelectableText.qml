import QtQuick

TextEdit {
    readOnly: true
    textFormat: TextEdit.AutoText
    wrapMode: Text.WordWrap
    selectByMouse: true
    onLinkActivated: Qt.openUrlExternally(hoveredLink)

    MouseArea {
        anchors.fill: parent
        acceptedButtons: Qt.NoButton // we don't want to eat clicks on the Text
        cursorShape: parent.hoveredLink ? Qt.PointingHandCursor : undefined
    }
}
