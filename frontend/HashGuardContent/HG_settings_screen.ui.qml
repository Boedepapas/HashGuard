

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

Rectangle {
    id: background
    width: Constants.width
    height: Constants.height
    color: "#c1c0c0"
    border.width: 1

    property string requestedNavigate: ""

    Rectangle {
        id: topBar
        color: "#f82b2b"
        radius: 20
        border.width: 0
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.leftMargin: 0
        anchors.rightMargin: 0
        anchors.topMargin: 0
        anchors.bottomMargin: 935
        topRightRadius: 0
        topLeftRadius: 0

        Text {
            id: titleHG
            text: qsTr("HashGuard")
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.leftMargin: 173
            anchors.rightMargin: 1290
            anchors.topMargin: 21
            anchors.bottomMargin: 22
            font.pixelSize: 80
            font.styleName: "Bold"
            font.family: "Tahoma"
            font.bold: true
        }

        Image {
            id: logoHG
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.leftMargin: 0
            anchors.rightMargin: 1745
            anchors.topMargin: 0
            anchors.bottomMargin: 0
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
                anchors.leftMargin: 0
                anchors.rightMargin: 0
                anchors.topMargin: 0
                anchors.bottomMargin: 0
                onClicked: background.requestedNavigate = "home"
            }
        }

        Rectangle {
            id: pagebar
            color: "#d62626"
            radius: 20
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.leftMargin: 684
            anchors.rightMargin: 36
            anchors.topMargin: 12
            anchors.bottomMargin: 13

            Rectangle {
                id: homepagebuttonImage
                color: "#ffffff"
                radius: 20
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.leftMargin: 15
                anchors.rightMargin: 903
                anchors.topMargin: 10
                anchors.bottomMargin: 10

                Text {
                    id: homepagebuttonText
                    text: qsTr("Home")
                    anchors.fill: parent
                    font.pixelSize: 50
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    font.styleName: "Bold"
                    font.family: "Tahoma"
                }

                MouseArea {
                    id: home_page_mouse_area
                    x: -15
                    y: -10
                    anchors.fill: parent
                    onClicked: background.requestedNavigate = "home"
                }
            }

            Rectangle {
                id: logspagebuttonImage
                color: "#ffffff"
                radius: 20
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.leftMargin: 311
                anchors.rightMargin: 607
                anchors.topMargin: 10
                anchors.bottomMargin: 10

                Text {
                    id: logspagebuttonText
                    text: qsTr("Logs and Alerts")
                    anchors.fill: parent
                    font.pixelSize: 43
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    wrapMode: Text.Wrap
                    font.styleName: "Bold"
                    font.family: "Tahoma"
                }

                MouseArea {
                    id: logs_page_mouse_area
                    anchors.fill: parent
                    onClicked: background.requestedNavigate = "logs"
                }
            }

            Rectangle {
                id: quarantinepagebuttonImage
                color: "#ffffff"
                radius: 20
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.leftMargin: 607
                anchors.rightMargin: 311
                anchors.topMargin: 10
                anchors.bottomMargin: 10

                Text {
                    id: quarantinepagebuttonText
                    text: qsTr("Quarantine")
                    anchors.fill: parent
                    font.pixelSize: 45
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    font.styleName: "Bold"
                    font.family: "Tahoma"
                }

                MouseArea {
                    id: quarantine_page_mouse_area
                    anchors.fill: parent
                    onClicked: background.requestedNavigate = "quarantine"
                }
            }

            Rectangle {
                id: settingspagebuttonImage
                color: "#c1c0c0"
                radius: 20
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.leftMargin: 903
                anchors.rightMargin: 15
                anchors.topMargin: 10
                anchors.bottomMargin: 10

                Text {
                    id: settingspagebuttonText
                    text: qsTr("Settings")
                    anchors.fill: parent
                    font.pixelSize: 50
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    font.styleName: "Bold"
                    font.family: "Tahoma"
                }
            }
        }
    }

    Rectangle {
        id: settings_page
        color: "#ffffff"
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.leftMargin: 76
        anchors.rightMargin: 76
        anchors.topMargin: 197
        anchors.bottomMargin: 84

        Text {
            id: env_status
            text: qsTr("Environment File Status : ")
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.leftMargin: 32
            anchors.rightMargin: 26
            anchors.topMargin: 38
            anchors.bottomMargin: 661
            font.pixelSize: 40
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            font.styleName: "Bold"
            font.family: "Tahoma"
        }

        Text {
            id: quarantine_folder
            text: qsTr("Quarantine Folder : ")
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.leftMargin: 32
            anchors.rightMargin: 26
            anchors.topMargin: 149
            anchors.bottomMargin: 550
            font.pixelSize: 40
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            font.styleName: "Bold"
            font.family: "Tahoma"
        }

        Text {
            id: log_status
            text: qsTr("Log System Status : ")
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.leftMargin: 32
            anchors.rightMargin: 26
            anchors.topMargin: 266
            anchors.bottomMargin: 433
            font.pixelSize: 40
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            font.styleName: "Bold"
            font.family: "Tahoma"
        }

        Rectangle {
            id: set_env
            color: "#c1c0c0"
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.leftMargin: 77
            anchors.rightMargin: 1210
            anchors.topMargin: 479
            anchors.bottomMargin: 133

            Button {
                id: set_env_button
                text: qsTr("Set Environment File")
                anchors.fill: parent
                font.pointSize: 25
                font.weight: Font.Bold
                font.bold: true
                font.family: "Tahoma"
                display: AbstractButton.TextOnly
            }
        }

        Rectangle {
            id: set_quar
            color: "#c1c0c0"
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.leftMargin: 644
            anchors.rightMargin: 643
            anchors.topMargin: 479
            anchors.bottomMargin: 133

            Button {
                id: set_quar_button
                text: qsTr("Set Quarantine Folder")
                anchors.fill: parent
                font.pointSize: 25
                font.bold: true
                font.family: "Tahoma"
            }
        }

        Rectangle {
            id: update
            color: "#c1c0c0"
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.leftMargin: 1208
            anchors.rightMargin: 79
            anchors.topMargin: 479
            anchors.bottomMargin: 133

            Button {
                id: update_button
                text: qsTr("Update Settings")
                anchors.fill: parent
                font.pointSize: 25
                font.bold: true
                font.family: "Tahoma"
            }
        }
    }
}
