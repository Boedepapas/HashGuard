import QtQuick
import QtQuick.Controls
import HG_logs_screen_ui

HG_logs_screen_ui {
    id: logsScreen
    anchors.fill: parent

    // Logic part
    home_page_mouse_area.onClicked: {
        root.currentPage = "HomeScreen.qml"
    }
    settings_page_mouse_area.onClicked: {
        root.currentPage = "SettingsScreen.qml"
    }
    quarantine_page_mouse_area.onClicked: {
        root.currentPage = "QuarantineScreen.qml"
    }
    homeScreen.onClicked: {
        root.currentPage = "HomeScreen.qml"
    }
    ScrollView {
        id: logs_scroll_view
        anchors.fill: logs_menu
        TextArea {
            id: archive_logs_text
            width: parent.width
            wrapMode: Text.Wrap
            readOnly: true
            font.pixelSize: 20
            //populate with logs from backend
            archive_logs_text.text = backend.log.getAlertLogsText()
        }
        ListView {
            id: live_log
            anchors.fill: alerts_menu
            model: backend.log.getLogsModel()
            delegate: ItemDelegate{
                text: model.displaytext
                onClicked: {
                backend.log.openLogFile(model.filepath)
                }
            }
        }
    }
}