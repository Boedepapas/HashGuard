import QtQuick
import QtQuick.Controls
import HG_settings_screen_ui

HG_settings_screen_ui {
    id: settingsScreen
    anchors.fill: parent

    // Logic part
    home_page_mouse_area.onClicked: {
        root.currentPage = "HomeScreen.qml"
    }
    quarantine_page_mouse_area.onClicked: {
        root.currentPage = "QuarantineScreen.qml"
    }
    logs_page_mouse_area.onClicked: {
        root.currentPage = "LogsScreen.qml"
    }
    homeScreen.onClicked: {
        root.currentPage = "HomeScreen.qml"
    }
    //settings save button logic

}