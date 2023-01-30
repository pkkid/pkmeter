import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.3

ApplicationWindow {
  id: settings
  title: "PKMeter Settings"
  visible: true
  width: 300
  flags: Qt.WindowTitleHint |
    Qt.WindowMinimizeButtonHint

  Flow {
    id: header_focused_container
    anchors.fill: parent
    anchors.margins: 10
    flow: Flow.TopToBottom

    Row { 
      height: 100
      Text { text: "Hi Mom!" }
    }

    Row {
      id: buttonRow
      // anchors.bottom: parent.bottom
      // anchors.right: parent.right
      spacing: 5

      RoundButton {
        width: 60
        height: 30
        text: "Cancel"
        radius: 5
        onClicked: {
          settings.close()
        }
      }
      RoundButton {
        width: 60
        height: 30
        text: "Apply"
        radius: 5
      }
      RoundButton {
        width: 60
        height: 30
        text: "Save"
        radius: 5
      }
    }


  }
}
