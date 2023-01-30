import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.3
import "settings"

ApplicationWindow {
  id: settingsWindow
  title: "PKMeter Settings"
  visible: true
  width: 300
  flags: Qt.WindowTitleHint |
    Qt.WindowMinimizeButtonHint

  // Desktop Window Content
  Item {
    anchors.fill: parent
    anchors.margins: 10
    ColumnLayout {
      anchors.fill: parent
      Layout.alignment: Qt.AlignTop
      
      // Filler Row
      Item {
        Layout.fillWidth: true
        Layout.fillHeight: true
      }

      // Button Row
      RowLayout {
        id: buttonRow
        Layout.alignment: Qt.AlignRight | Qt.AlignTop
        Layout.maximumHeight: 30
        Layout.minimumHeight: 30
        FormButton {
          text: "Cancel"
          onClicked: {
            settingsWindow.close()
          }
        }
        FormButton {
          text: "Apply"
        }
        FormButton {
          text: "Save"
          highlighted: true
        }
      }

    }
  }
}
