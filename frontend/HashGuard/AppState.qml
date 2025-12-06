// AppState.qml
pragma Singleton
import QtQuick 2.15

QtObject {
    // Backend-driven SSOT properties
    property bool backendConnected: false
    property string backendVersion: ""
    property bool serviceRunning: false // is backend service running
    property string activeHash: ""
    property int errorCount: 0
    //Page-specific properties
    //Home page properties
    property bool isScanning: false // is backend currently scanning
    property int newQuarantineCount: 0 // number of new files in quarantine
    property int newFilesScanned: 0 // number of new files scanned
    //logs page properties
    property var alertList: [] // list of current alerts
    property var logEntries: [] // recent log entries
    property string logText: ""
    property string alertText: ""
    //quarantine page properties
    property var quarantineItems: [{id: "file1" , name: "Quarantined file1", timestamp:"12/5/2025"},{id: "file2" , name: "Quarantined file2", timestamp:"12/5/2025"}] //{id: "file1" , name: "Quarantined file1", timestamp:"12/5/2025"}
    property int quarantineItemCount: 1
    property string deleteFileID: ""
    // items in quarantine
    //settings page properties

    
    //Settings properties
    property var settings: ({})
    //Settings file status properties
    property bool settingsLoaded: false
    property bool settingsMissing: false
    property bool settingsEditMode: false
    property var settingsValidationErrors: []
    property string settingsSaveStatus: "idle" // "idle" | "saving" | "success" | "error"
    //convenience properties for settings
    property string watchPath: settings.watch_path || "./downloads"
    property string quarantinePath: settings.quarantine_path || "./quarantine"
    property var allowedExtensions: settings.allowed_extensions || [".exe",".msi",".zip",".7z",".pdf",".docx",".js"]
    property var priorityMap: settings.priority_map || ({".exe":10,".msi":9,".zip":7,".7z":7,".pdf":5})

    function openFolder(path) {
            if (!path) {
                console.warn("[AppState] openFolder called with empty path")
                return
            }
            // Normalize slashes and ensure no accidental double slashes
            var normalized = path.replace(/\\/g, "/")
            // Ensure it starts with a drive letter or slash; adjust if needed
            if (normalized.indexOf(":/") === -1 && normalized.indexOf("/") !== 0) {
                // if you store relative paths, convert to absolute here
            }
            var url = "file:///" + normalized
            console.log("[AppState] openFolder ->", url)
            Qt.openUrlExternally(url)
        }


 //property string activePage: "home" | "logs" | "settings" | "quarantine"

    // Signals for events

    signal userDataChanged(var newData)
}
