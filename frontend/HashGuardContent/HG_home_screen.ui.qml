

/*
This is a UI file (.ui.qml) that is intended to be edited in Qt Design Studio only.
It is supposed to be strictly declarative and only uses a subset of QML. If you edit
this file manually, you might introduce QML code that is not supported by Qt Design Studio.
Check out https://doc.qt.io/qtcreator/creator-quick-ui-forms.html for details on .ui.qml files.
*/
import QtQuick
import QtQuick.Controls
import HashGuard
import QtQuick.Studio.DesignEffects
import QtQuick.Layouts

Rectangle {
    id: background
    anchors.fill: parent
    color: "#c1c0c0"
    border.width: 1

    property string requestedNavigation: ""
    signal requestedNavigationSignal(string key)
    property alias startStopButton: start_stop_button
    property alias startImage: start_image
    property alias stopImage: stop_image
    property alias homeInfoText: home_info_text

    Rectangle {
        id: topBar
        color: "#f82b2b"
        radius: 20
        border.width: 0
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        height: Math.max(48, Math.min(parent.height * 0.08, 120))
        topRightRadius: 0
        topLeftRadius: 0

        Text {
            id: titleHG
            text: qsTr("HashGuard")
            anchors.left: logoHG.right
            anchors.verticalCenter: parent.verticalCenter
            anchors.leftMargin: 12
            font.pixelSize: Math.max(20, Math.min(parent.height * 0.75, 80))
            font.styleName: "Bold"
            font.family: "Tahoma"
            font.bold: true
        }

        Image {
            id: logoHG
            anchors.left: parent.left
            anchors.verticalCenter: parent.verticalCenter
            anchors.leftMargin: 12
            height: parent.height
            source: "../HG_Logo.png"
            fillMode: Image.PreserveAspectFit

            Button {
                id: homeScreen
                opacity: 0
                visible: true
                text: qsTr("Button")
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.bottom: parent.bottom
            }
        }

        Rectangle {
            id: pagebar
            color: "#d62626"
            radius: 20
            anchors {
                left: titleHG.right
                leftMargin: 12
                right: parent.right
                top: parent.top
                bottom: parent.bottom
            }
            // height should be relative to topBar (or pagebar parent)
            height: topBar.height * 0.7

            RowLayout {
                id: rowLayout
                anchors.fill: parent
                anchors.margins: 8
                spacing: 12

                // each child will take an equal share of the row
                Rectangle {
                    id: homepagebuttonImage
                    color: "#c1c0c0"
                    radius: 12
                    Layout.fillWidth: true
                    Layout.preferredHeight: parent.height
                    height: Layout.preferredHeight

                    Text {
                        anchors.fill: parent
                        text: qsTr("Home")
                        font.pixelSize: Math.max(12, Math.round(
                                                     parent.height * 0.65))
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        font.styleName: "Bold"
                        font.family: "Tahoma"
                        font.bold: true
                    }
                }

                Rectangle {
                    id: logspagebuttonImage
                    color: "#ffffff"
                    radius: 12
                    Layout.fillWidth: true
                    Layout.preferredHeight: parent.height

                    Text {
                        anchors.fill: parent
                        text: qsTr("Logs and Alerts")
                        font.pixelSize: Math.max(12, Math.round(
                                                     parent.height * 0.32))
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        wrapMode: Text.Wrap
                        font.styleName: "Bold"
                        font.family: "Tahoma"
                        font.bold: true
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: background.requestedNavigation = "logs"
                    }
                }

                Rectangle {
                    id: quarantinepagebuttonImage
                    color: "#ffffff"
                    radius: 12
                    Layout.fillWidth: true
                    Layout.preferredHeight: parent.height

                    Text {
                        anchors.fill: parent
                        text: qsTr("Quarantine")
                        font.pixelSize: Math.max(12, Math.round(
                                                     parent.height * 0.32))
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        font.styleName: "Bold"
                        font.family: "Tahoma"
                        font.bold: true
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: background.requestedNavigation = "quarantine"
                    }
                }

                Rectangle {
                    id: settingspagebuttonImage
                    color: "#ffffff"
                    radius: 12
                    Layout.fillWidth: true
                    Layout.preferredHeight: parent.height

                    Text {
                        anchors.fill: parent
                        text: qsTr("Settings")
                        font.pixelSize: Math.max(12, Math.round(
                                                     parent.height * 0.35))
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        font.styleName: "Bold"
                        font.family: "Tahoma"
                        font.bold: true
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: background.requestedNavigation = "settings"
                    }
                }
            }
        }
    }

    Rectangle {
        id: startmenu
        color: "#e8e7e7"
        border.width: 3
        anchors.left: parent.left
        anchors.top: topBar.bottom
        anchors.bottom: parent.bottom
        width: parent.width / 2
        anchors.topMargin: 100

        Image {
            id: start_image
            visible: !AppState.isScanning
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            source: "../start_image.png"
            rotation: -270
            fillMode: Image.PreserveAspectFit
        }

        Image {
            id: stop_image
            visible: AppState.isScanning
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            source: "../stop_image.png"
            rotation: -270
            fillMode: Image.PreserveAspectFit
        }

        Button {
            id: start_stop_button
            opacity: 0
            visible: true
            text: qsTr("Button")
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            wheelEnabled: false
            hoverEnabled: false
            checkable: true
        }
    }

    Rectangle {
        id: home_info_menu
        color: "#e8e7e7"
        border.width: 3
        anchors.right: parent.right
        anchors.top: topBar.bottom
        anchors.bottom: parent.bottom
        anchors.topMargin: 100
        width: parent.width / 2

        Text {
            id: home_info_text
            text: qsTr("New Logs: \nNew Files in Quarantine: ")
            anchors.fill: parent
            font.pixelSize: Math.max(40, Math.min(parent.height * 0.050, 120))
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            wrapMode: Text.WordWrap
            padding: 10
            font.family: "Tahoma"
        }
    }
}
