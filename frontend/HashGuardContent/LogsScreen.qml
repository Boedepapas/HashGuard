// LogsScreen.qml
import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: wrapper
    anchors.fill: parent

    // Forward navigation to App.qml
    signal requestNavigate(string pageFile)

    Loader {
        id: uiLoader
        anchors.fill: parent
        source: "HG_logs_screen.ui.qml"
    }

    Connections {
        target: uiLoader
        onStatusChanged: {
            if (uiLoader.status === Loader.Ready) {
                var ui = uiLoader.item
                if (!ui) return

                // Listen for property-based navigation requests
                if (!ui.__navHandlerAttached && ui.requestedNavigationChanged) {
                    ui.__navHandlerAttached = true
                    ui.requestedNavigationChanged.connect(function() {
                        var key = ui.requestedNavigation
                        if (!key) return
                        switch (key) {
                        case "home":       wrapper.requestNavigate("HomeScreen.qml"); break
                        case "settings":   wrapper.requestNavigate("SettingsScreen.qml"); break
                        case "quarantine": wrapper.requestNavigate("QuarantineScreen.qml"); break
                        default:           wrapper.requestNavigate(key) // allow direct filenames if ever used
                        }
                        ui.requestedNavigation = "" // clear for future clicks
                    })
                }
            } else if (uiLoader.status === Loader.Error) {
                console.error("Failed to load logs UI:", uiLoader.source)
            }
        }
    }
}
