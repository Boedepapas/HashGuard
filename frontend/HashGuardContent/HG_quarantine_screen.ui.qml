

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
    width: Constants.width
    height: Constants.height
    color: "#c1c0c0"
    border.width: 1

    property string requestedNavigation: ""
    property string deletefileId: ""
    property int deletebuttonIndex: 0
    property string selectedFileName: ""
    property alias openFolderButton: deleteBox.openFolderButton
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
                onClicked: background.requestedNavigate = "home"
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
            height: topBar.height * 0.7

            RowLayout {
                id: rowLayout
                anchors.fill: parent
                anchors.margins: 8
                spacing: 12
                Rectangle {
                    id: homepagebuttonImage
                    color: "#ffffff"
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

                    MouseArea {
                        id: home_page_mouse_area
                        anchors.fill: parent
                        onClicked: background.requestedNavigation = "home"
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
                        id: logs_page_mouse_area
                        anchors.fill: parent
                        onClicked: background.requestedNavigation = "logs"
                    }
                }

                Rectangle {
                    id: quarantinepagebuttonImage
                    color: "#c1c0c0"
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
                        id: settings_page_mouse_area
                        anchors.fill: parent
                        onClicked: background.requestedNavigation = "settings"
                    }
                }
            }
        }
    }

    Rectangle {
        id: quarantine_area
        color: "#e8e7e7"
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        height: 700
        width: 1200

        property int visibleItemCount: AppState.quarantineItemCount

        ScrollView {
            id: quarantineScroll
            anchors.fill: parent
            clip: true

            Column {
                id: filesColumn
                width: parent.width
                spacing: Math.max(8, quarantine_area.height * 0.02)
                anchors.margins: 12
                padding: 8

                Repeater {
                    id: filesRepeater
                    model: AppState.quarantineItems

                    delegate: Rectangle {
                        property var fileInfo: modelData
                        property int fileIndex: index
                        signal deleteRequested(int index, string fileID)

                        id: fileRect
                        color: "#ffffff"
                        radius: 8
                        width: filesColumn.width - 32
                        height: Math.max(56, quarantine_area.height * 0.11)
                        anchors.horizontalCenter: filesColumn.horizontalCenter
                        border.color: "#dcdcdc"
                        border.width: 1
                        anchors.margins: 8

                        property real iconSize: Math.max(36,
                                                         fileRect.height * 0.6)

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 12
                            spacing: Math.max(12, fileRect.height * 0.08)

                            // Optional left icon or checkbox (remove if you don't want anything on the left)
                            Rectangle {
                                id: leftPlaceholder

                                Layout.preferredWidth: iconSize
                                Layout.preferredHeight: iconSize
                                color: "#f6f6f6"
                                radius: 6
                                Layout.alignment: Qt.AlignVCenter
                                Button {
                                    property bool selected: false
                                    id: trashBtn

                                    width: 45
                                    height: 45
                                    hoverEnabled: false
                                    opacity: 0
                                }
                            }

                            // Text column takes remaining space and pushes the trash button to the right
                            Column {
                                Layout.fillWidth: true
                                spacing: 4
                                Layout.alignment: Qt.AlignVCenter

                                Text {
                                    id: fileTitle
                                    text: fileInfo.name
                                    font.pixelSize: Math.max(
                                                        12,
                                                        fileRect.height * 0.28)
                                    font.family: "Tahoma"
                                    font.bold: true
                                    elide: Text.ElideRight
                                    wrapMode: Text.NoWrap
                                }

                                Text {
                                    id: fileMeta
                                    text: fileInfo.timestamp
                                    font.pixelSize: Math.max(
                                                        10,
                                                        fileRect.height * 0.20)
                                    color: "#666666"
                                    elide: Text.ElideRight
                                    wrapMode: Text.NoWrap
                                }
                            }
                        }

                        // allow the ScrollView's flickable to steal drags so scrolling works
                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            preventStealing: false
                        }
                    } // end delegate Rectangle
                } // end Repeater
            } // end Column
        } // end ScrollView
    } // end quarantine_area Rectangle
    Rectangle {
        id: deleteBox
        property alias openFolderButton: openFolderButton
        anchors {
            top: quarantine_area.bottom
            topMargin: 50
            horizontalCenter: quarantine_area.horizontalCenter
        }
        height: 100
        width: 650
        Text {
            anchors {
                top: parent.top
                bottom: parent.bottom
                left: parent.left
                right: openFolderButton.left
            }
            text: qsTr("Quarantine Folder")
            font.pixelSize: 50
            font.bold: true
            verticalAlignment: Text.AlignVCenter
            padding: 15
            font.family: "Tahoma"
        }

        Button {
            id: openFolderButton
            objectName: "openFolderButton"
            anchors {
                top: parent.top
                bottom: parent.bottom
                right: parent.right
            }

            text: qsTr("Open")
            font.family: "Tahoma"
            font.pixelSize: 50
            font.bold: true
        }
    }
}
