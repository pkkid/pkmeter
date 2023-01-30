import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.3
import "desktop"

ApplicationWindow {
  id: desktopWindow
  color: "transparent"
  height: 800
  title: "PKMeter"
  visible: true
  width: 200
  x: 100
  y: 100
  flags: Qt.Tool |
    //Qt.WindowStaysOnBottomHint |
    Qt.CustomizeWindowHint |
    Qt.FramelessWindowHint |
    Qt.NoDropShadowWindowHint
  
  // Load the Material Design Icons webfont
  FontLoader {
    id: mdi
    source: "resources/mdi-v7.1.96.ttf"
  }

  // Show and Hide the Toolbar when entering the app
  MouseArea {
    anchors.fill: parent
    hoverEnabled: true
    onEntered: toolbar.opacity = 1
    onExited: {
      if (mouseX <= 8 || mouseX >= width-8 || mouseY <= 8 || mouseY >= height-8) {
        toolbar.opacity = 0
      }
    }
  }

  // Desktop Window Background
  Rectangle {
    id: bg
    anchors.fill: parent
    color: "black"
    opacity: 0.5
  }

  // Desktop Window Content
  Item {
    anchors.fill: parent
    anchors.margins: 10
    ColumnLayout {
      anchors.fill: parent
      Layout.alignment: Qt.AlignTop
      
      Toolbar {
        id: toolbar
        opacity: 0
      }
    }
  }
}
