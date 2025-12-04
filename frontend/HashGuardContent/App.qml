import QtQuick
import HashGuard

Window {
    id: root
    visible: true
    title: "HashGuard"
    width: 800
    height: 600

    Loader{
        id: pageLoader
        anchors.fill: parent
        source: currentPage
    }
    property string currentPage: "HomeScreen.qml"
}

