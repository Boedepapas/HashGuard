import QtQuick 2.15
import QtQuick.Window 2.15
import HashGuard 1.0

Window {
    id: root
    visible: true
    title: "HashGuard"
    width: Constants.width
    height: Constants.height

    // Single source of truth for navigation
    property string currentPage: "HomeScreen.qml"

    // Map to store handler functions on the App side (do not add dynamic properties to loaded pages)
    property var navHandlers: ({})
    // Optional: remember last loaded source for debugging
    property string lastLoadedSource: ""

    Loader {
        id: pageLoader
        anchors.fill: parent
        source: currentPage

        onLoaded: {
            console.log("[App] loaded ->", pageLoader.source)
            var page = pageLoader.item
            if (!page) {
                console.error("[App] loaded but pageLoader.item is null")
                return
            }

            // Use the loader source as a key for handler storage
            var key = pageLoader.source || "__unknown_page__"
            lastLoadedSource = key

            // If the page exposes a requestNavigate signal, wire it up
            if (page.requestNavigate) {
                // If we previously stored a handler for this key, try to disconnect it from the current page
                if (navHandlers[key]) {
                    try {
                        // Attempt to disconnect the old handler from this page (safe to ignore errors)
                        page.requestNavigate.disconnect(navHandlers[key])
                        console.log("[App] disconnected previous handler for", key)
                    } catch (e) {
                        // ignore disconnect errors
                    }
                }

                // Create a new handler function and store it on the App side
                var handler = function(pageFile) {
                    console.log("[App] requestNavigate received ->", pageFile)
                    // Validate pageFile before assigning
                    if (typeof pageFile === "string" && pageFile.length > 0) {
                        root.currentPage = pageFile
                    } else {
                        console.warn("[App] requestNavigate received invalid pageFile ->", pageFile)
                    }
                }
                navHandlers[key] = handler

                // Connect the handler to the page's signal
                try {
                    page.requestNavigate.connect(handler)
                    console.log("[App] connected requestNavigate on", key)
                } catch (e) {
                    console.error("[App] failed to connect requestNavigate on", key, e)
                }
            } else {
                console.log("[App] loaded page has no requestNavigate signal:", pageLoader.source)
            }
        }

        onStatusChanged: {
            console.log("[App] pageLoader status:", pageLoader.status)
            if (pageLoader.status === Loader.Error) {
                console.error("[App] Loader error loading", pageLoader.source, pageLoader.errorString())
            }
        }
    }

    // Keep console visible for navigation changes
    onCurrentPageChanged: {
        console.log("[App] currentPage ->", currentPage)
        // Update the loader source to navigate
        if (pageLoader.source !== currentPage) {
            pageLoader.source = currentPage
        }
    }
}
