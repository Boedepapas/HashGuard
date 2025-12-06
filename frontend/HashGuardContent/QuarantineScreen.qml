import QtQuick 2.15
import QtQuick.Controls 2.15
import HashGuard

Item {
    id: wrapper
    anchors.fill: parent

    // wrapper forwards navigation requests to App.qml
    signal requestNavigate(string pageFile)
    function requestOpenQuarantine() {
        console.log("[UI] requestOpenQuarantine -> calling backend")
        var xhr = new XMLHttpRequest()
        xhr.open("POST", "http://127.0.0.1:5001/open-quarantine")
        xhr.setRequestHeader("Content-Type", "application/json")
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                console.log("[UI] open-quarantine response", xhr.status, xhr.responseText)
                try {
                    var r = JSON.parse(xhr.responseText)
                    if (r.ok) {
                        // success feedback if desired
                    } else {
                        console.error("[UI] backend error:", r.error)
                    }
                } catch (e) {
                    console.error("[UI] invalid response", e)
                }
            }
        }
        xhr.send() // no body required
    }


    function deleteQuarantineItem(index, fileId) {
            console.log("wrapper.deleteQuarantineItem", index, fileId)
            // optimistic removal example:
            var removed = AppState.quarantineItems.splice(index, 1)
            // forward to daemon via AppState or Backend
            if (AppState.deleteQuarantineFile) {
                AppState.deleteQuarantineFile(fileId)
            } else if (Backend && Backend.deleteQuarantineFile) {
                Backend.deleteQuarantineFile(fileId)
            } else {
                // fallback: log or REST call
                console.warn("No backend bridge available")
            }
    }
    function wireDelegate(d, idx) {
            if (!d || !d.trashBtn || d.__trashWired) return
            // connect trash click -> emit delegate signal and call wrapper
            d.trashBtn.clicked.connect((function(item, index) {
                return function() {
                    // emit delegate signal (optional)
                    if (item.deleteRequested) item.deleteRequested(index, item.fileInfo.id)
                    // call centralized delete logic
                    wrapper.deleteQuarantineItem(index, item.fileInfo.id)
                }
            })(d, idx))
            d.__trashWired = true
    }
    // wire all current delegates in the repeater
    function wireAllDelegates() {
        var ui = uiLoader.item
        if (!ui || !ui.filesRepeater) return
        var rep = ui.filesRepeater
        if (rep.count === undefined || !rep.itemAt) return
        for (var i = 0; i < rep.count; ++i) {
            var d = rep.itemAt(i)
            wireDelegate(d, i)
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

    property var rewireAttachedItems: []

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
                // --- wire open button once per ui instance ---
                if (!ui.__openButtonWired) {
                    if (ui.openFolderButton) {
                        console.log("[QuarantineLoader] wiring openFolderButton")
                        ui.openFolderButton.clicked.connect(function() {
                            console.log("[QuarantineLoader] openFolderButton clicked")
                            // call wrapper function that talks to backend
                            wrapper.requestOpenQuarantine()
                        })
                        ui.__openButtonWired = true
                    } else {
                        console.warn("[QuarantineLoader] ui does not expose openFolderButton")
                        }
                    } else {
                        console.log("[QuarantineLoader] open button already wired for this ui instance")
                        }

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
            // place this after your navigation wiring (still inside onStatusChanged when Loader.Ready)
        } 
    }
}
