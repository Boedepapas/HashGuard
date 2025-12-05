import QtQuick
import QtQuick.Controls
import HG_home_screen_ui

HG_home_screen_ui {
    id: homeScreen
    anchors.fill: parent

    // Logic part
   
    logs_page_mouse_area.onClicked: {
        root.currentPage = "LogsScreen.qml"
    }
    settings_page_mouse_area.onClicked: {
        root.currentPage = "SettingsScreen.qml"
    }
    quarantine_page_mouse_area.onClicked: {
        root.currentPage = "QuarantineScreen.qml"
    }
    //need to add pause and start fuctionality to backend and connect it here
    start_stop_button.onClicked: {
        if(!backend.monitor.isScanning()){
            backend.monitor.startMonitoring()
            start_image.visible = false
            stop_image.visible = true
            backend.log.addLog("Monitoring started.")
        }
        if(backend.monitor.isScanning()){
            backend.monitor.stopMonitoring()
            start_image.visible = true
            stop_image.visible = false
            backend.log.addLog("Monitoring stopped.")
        }
    }
    // need to add a function that updates these values when something changes. like a backend function that sends signal to ui to update if ui is open
    home_info_text.text = "New Files in Quarantine: " + backend.log.getNewQuarantineCount().toString() + "\nTotal Files Scanned: " + backend.log.getTotalScannedCount().toString()
    // need to add more text to this info box later
}


