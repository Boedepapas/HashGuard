import QtQuick 2.15
import QtQuick.Controls 2.15
import HashGuard

Item {
    id: wrapper
    anchors.fill: parent

    // wrapper forwards navigation requests to App.qml
    signal requestNavigate(string pageFile)

    Loader {
        id: uiLoader
        anchors.fill: parent
        source: "HG_home_screen.ui.qml"
    }

    // prevent duplicate wiring if loader reloads
    property bool handlersAttached: false

    // track ui instances we've already wired (do not add properties to ui itself)
    property var navAttachedItems: []

    Connections {
        target: uiLoader
        onStatusChanged: {
            console.log("[HomeScreen] uiLoader.status ->", uiLoader.status)
            if (uiLoader.status === Loader.Ready) {
                var ui = uiLoader.item
                if (!ui) {
                    console.error("[HomeScreen] uiLoader.item is null or undefined")
                    return
                }
                console.log("[HomeScreen] UI loaded:", ui)

                // --- Navigation wiring: attach once per ui instance ---
                if (navAttachedItems.indexOf(ui) === -1) {
                    navAttachedItems.push(ui)
                    console.log("[HomeScreen] Attaching requestedNavigationChanged handler for ui:", ui)

                    if (ui.requestedNavigationChanged) {
                        ui.requestedNavigationChanged.connect(function() {
                            console.log("[HomeScreen] requestedNavigationChanged fired. value ->", ui.requestedNavigation)
                            var key = ui.requestedNavigation
                            if (!key) return

                            // map semantic keys to actual page filenames
                            switch (key) {
                            case "home":
                                console.log("[HomeScreen] mapping 'home' -> HomeScreen.qml")
                                wrapper.requestNavigate("HomeScreen.qml")
                                break
                            case "logs":
                                console.log("[HomeScreen] mapping 'logs' -> LogsScreen.qml")
                                wrapper.requestNavigate("LogsScreen.qml")
                                break
                            case "settings":
                                console.log("[HomeScreen] mapping 'settings' -> SettingsScreen.qml")
                                wrapper.requestNavigate("SettingsScreen.qml")
                                break
                            case "quarantine":
                                console.log("[HomeScreen] mapping 'quarantine' -> QuarantineScreen.qml")
                                wrapper.requestNavigate("QuarantineScreen.qml")
                                break
                            default:
                                console.log("[HomeScreen] forwarding raw key ->", key)
                                wrapper.requestNavigate(key)
                            }

                            // clear so subsequent clicks trigger the change again
                            ui.requestedNavigation = ""
                            console.log("[HomeScreen] cleared ui.requestedNavigation")
                        })
                    } else {
                        console.warn("[HomeScreen] ui does not expose requestedNavigationChanged")
                    }
                } else {
                    console.log("[HomeScreen] navigation handler already attached for this ui instance")
                }

                // --- Other handlers (start/stop button, info text) ---
                // Attach these once per wrapper load (handlersAttached guard)
                if (!handlersAttached) {
                    handlersAttached = true
                    console.log("[HomeScreen] Attaching other UI handlers")

                    var startBtn = ui.startStopButton ? ui.startStopButton : (ui.start_stop_button ? ui.start_stop_button : null)
                    var startImg = ui.startImage ? ui.startImage : (ui.start_image ? ui.start_image : null)
                    var stopImg  = ui.stopImage ? ui.stopImage : (ui.stop_image ? ui.stop_image : null)

                    console.log("[HomeScreen] startBtn:", startBtn, "startImg:", startImg, "stopImg:", stopImg)

                    if (startBtn) {
                        // Attach a single handler that toggles the AppState property
                        // Do not add dynamic properties to startBtn; rely on handlersAttached to avoid duplicates
                        startBtn.clicked.connect(function() {
                            console.log("[HomeScreen] startBtn clicked. AppState.scanning before ->", AppState.scanning)
                            AppState.scanning = !AppState.scanning
                            console.log("[HomeScreen] AppState.scanning after ->", AppState.scanning)
                        })
                        console.log("[HomeScreen] startBtn click handler attached")
                    } else {
                        console.warn("[HomeScreen] startBtn not found on UI")
                    }

                    // Update info text initially (consider dynamic updates later)
                    var infoText = ui.homeInfoText ? ui.homeInfoText : (ui.home_info_text ? ui.home_info_text : null)
                    if (infoText && typeof AppState !== "undefined" && AppState.newQuarantineCount !== undefined) {
                        infoText.text = "New Files in Quarantine: " + AppState.newQuarantineCount
                        console.log("[HomeScreen] Set initial infoText ->", infoText.text)
                    } else {
                        console.log("[HomeScreen] infoText not found or AppState missing")
                    }
                } else {
                    console.log("[HomeScreen] handlersAttached already true, skipping re-attach")
                }
            } else if (uiLoader.status === Loader.Error) {
                console.error("[HomeScreen] Failed to load home UI:", uiLoader.source, uiLoader.errorString())
            } else {
                console.log("[HomeScreen] uiLoader.status changed to", uiLoader.status)
            }
        }
    }
}
