import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.3
import "components"


ApplicationWindow {
  id: "pkmeter"
  color: "transparent"
  height: 800
  title: "PKMeter"
  visible: true
  width: 200
  flags: Qt.Tool |
    Qt.FramelessWindowHint |
    // Qt.WindowStaysOnBottomHint |
    Qt.NoDropShadowWindowHint |
    Qt.CustomizeWindowHint

  // Load the Material Design Icons webfont
  FontLoader {
    id: mdi
    source: "mdi-v7.1.96.ttf"
  }

  // Show and Hide the Toolbar when entering the app
  MouseArea {
    anchors.fill: parent
    hoverEnabled: true
    onEntered: {
      toolbarFadeOut.stop()
      toolbarFadeIn.start()
    }
    onExited: {
      if (mouseX <= 8 || mouseX >= width-8 || mouseY <= 8 || mouseY >= height-8) {
        toolbarFadeIn.stop()
        toolbarFadeOut.start()
      }
    }
  }
  NumberAnimation {
    id: toolbarFadeIn
    target: toolbar
    property: "opacity"
    to: 1
    duration: 200
  }
  NumberAnimation {
    id: toolbarFadeOut
    target: toolbar
    property: "opacity"
    to: 0
    duration: 200
  }

  // Main Background
  Rectangle {
    id: bg
    anchors.fill: parent
    color: "black"
    opacity: 0.5
  }

  // Main Content Area
  Rectangle {
    id: content
    anchors.fill: parent
    anchors.margins: 10
    color: "transparent"

    RowLayout {
      id: toolbar
      height: 15
      spacing: 8
      opacity: 0
      anchors.right: parent.right

      ToolbarIcon {
        text: "󰢻"  // cog
      }
      ToolbarIcon {
        text: "󰅖"  // close
        MouseArea {
          anchors.fill: parent
          cursorShape: Qt.PointingHandCursor
          onClicked: Qt.quit()
        }
      }
    }
  }

}
