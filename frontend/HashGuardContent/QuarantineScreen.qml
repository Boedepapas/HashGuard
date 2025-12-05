// QuarantineScreen.qml
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
        source: "HG_quarantine_screen.ui.qml"  // adjust the path if needed
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
                        case "home":     wrapper.requestNavigate("HomeScreen.qml"); break
                        case "settings": wrapper.requestNavigate("SettingsScreen.qml"); break
                        case "logs":     wrapper.requestNavigate("LogsScreen.qml"); break
                        default:         wrapper.requestNavigate(key)
                        }
                        // clear for future clicks
                        ui.requestedNavigation = ""
                    })
                }

                // Future: wire quarantine list/pagination here (no functionality now)
                // Example stubs for later:
                // - ui.quarantineRepeater.model = someArray.length
                // - ui.previous_button.onClicked = function() { /* paginate */ }
                // - ui.next_button.onClicked = function() { /* paginate */ }
            } else if (uiLoader.status === Loader.Error) {
                console.error("Failed to load quarantine UI:", uiLoader.source)
            }
        }
    }
}
