import QtQuick 2.15
import QtQuick.Layouts 1.3

RowLayout {
  Layout.fillWidth: true
  Layout.alignment: Qt.AlignRight | Qt.AlignTop
  Layout.maximumHeight: 16
  Layout.minimumHeight: 16

  Item {
    Layout.fillWidth: true
    Layout.fillHeight: true
  }
  ToolbarIcon {
    height: parent.height
    text: "󰢻"  // cog
    MouseArea {
      anchors.fill: parent
      cursorShape: Qt.PointingHandCursor
      onClicked: {
        var newWindow = Qt.createComponent("../settings.qml")
        var newWindowObject = newWindow.createObject(desktopWindow)
        newWindowObject.visible = true  
      }
    }
  }
  ToolbarIcon {
    height: parent.height
    text: "󰅖"  // close
    MouseArea {
      anchors.fill: parent
      cursorShape: Qt.PointingHandCursor
      onClicked: Qt.quit()
    }
  }
}
