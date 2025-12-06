import QtQuick 2.15
import QtQuick.Controls 2.15
import HashGuard

Item {
    id: wrapper
    anchors.fill: parent

    // wrapper forwards navigation requests to App.qml
    signal requestNavigate(string pageFile)


    function logQuarantineCount() {
            if (AppState.quarantineItems) {
                console.log("Quarantine count:", AppState.quarantineItems.length)
            }
        }

        function deleteByIndex(idx) {
            if (AppState.quarantineItems && idx >= 0 && idx < AppState.quarantineItems.length) {
                var file = AppState.quarantineItems[idx]
                console.log("Deleting file at index", idx, "with id", file.id)
                // remove from array
            }
        }


    Loader {
        id: uiLoader
        anchors.fill: parent
        source: "HG_quarantine_screen.ui.qml"
    }

    // prevent duplicate wiring if loader reloads
    property bool handlersAttached: false

    // track ui instances we've already wired (do not add properties to ui itself)
    property var navAttachedItems: []

    Connections {
        target: uiLoader
        onStatusChanged: {
            console.log("[QuarantineLoader] uiLoader.status ->", uiLoader.status)
            if (uiLoader.status === Loader.Ready) {
                var ui = uiLoader.item
                if (!ui) {
                    console.error("[QuarantineLoader] uiLoader.item is null or undefined")
                    return
                }
                console.log("[QuarantineLoader] UI loaded:", ui)

                // --- Navigation wiring: attach once per ui instance ---
                if (navAttachedItems.indexOf(ui) === -1) {
                    navAttachedItems.push(ui)
                    console.log("[QuarantineLoader] Attaching requestedNavigationChanged handler for ui:", ui)

                    if (ui.requestedNavigationChanged) {
                        ui.requestedNavigationChanged.connect(function() {
                            console.log("[QuarantineLoader] requestedNavigationChanged fired. value ->", ui.requestedNavigation)
                            var key = ui.requestedNavigation
                            if (!key) return

                            // map semantic keys to actual page filenames
                            switch (key) {
                            case "home":
                                wrapper.requestNavigate("HomeScreen.qml")
                                break
                            case "logs":
                                wrapper.requestNavigate("LogsScreen.qml")
                                break
                            case "settings":
                                wrapper.requestNavigate("SettingsScreen.qml")
                                break
                            case "quarantine":
                                wrapper.requestNavigate("QuarantineScreen.qml")
                                break
                            default:
                                wrapper.requestNavigate(key)
                            }

                            // clear so subsequent clicks trigger the change again
                            ui.requestedNavigation = ""
                        })
                    } else {
                        console.warn("[QuarantineLoader] ui does not expose requestedNavigationChanged")
                    }
                } else {
                    console.log("[QuarantineLoader] navigation handler already attached for this ui instance")
                }

                // --- Other handlers (start/stop button, info text, quarantine actions) ---
            }
        }
    }
}
