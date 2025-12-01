

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
                x: 0
                y: 0
                width: 175
                height: 145
                opacity: 0
                visible: true
                text: qsTr("Button")
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
                    anchors.fill: parent
                }
            }

            Rectangle {
                id: logspagebuttonImage
                color: "#c1c0c0"
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
                }
            }

            Rectangle {
                id: settingspagebuttonImage
                color: "#ffffff"
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

                MouseArea {
                    id: settings_page_mouse_area
                    anchors.fill: parent
                }
            }
        }
    }

    Rectangle {
        id: alerts_menu
        color: "#e8e7e7"
        border.width: 3
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.leftMargin: 983
        anchors.rightMargin: 33
        anchors.topMargin: 298
        anchors.bottomMargin: 79
        Text {
            id: alerts_info_text
            text: qsTr("Placement Text (Replace with Alert notifications or some other kind of info)")
            anchors.fill: parent
            font.pixelSize: 30
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
            topPadding: 10
            padding: 10
            font.family: "Tahoma"
        }

        MouseArea {
            id: alert_mouse_area
            anchors.fill: parent
        }
    }

    Rectangle {
        id: logs_menu
        color: "#e8e7e7"
        border.width: 3
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.leftMargin: 33
        anchors.rightMargin: 983
        anchors.topMargin: 298
        anchors.bottomMargin: 78
        Text {
            id: logs_info_text
            text: qsTr("Placement Text (Replace with Alert notifications or some other kind of info)")
            anchors.fill: parent
            font.pixelSize: 30
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
            topPadding: 10
            padding: 10
            font.family: "Tahoma"
        }

        MouseArea {
            id: logs_mouse_area
            anchors.fill: parent
        }
    }

    Text {
        id: text1
        text: qsTr("Logs")
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.leftMargin: 33
        anchors.rightMargin: 983
        anchors.topMargin: 164
        anchors.bottomMargin: 796
        font.pixelSize: 80
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        font.bold: true
        font.family: "Tahoma"
    }

    Text {
        id: text2
        text: qsTr("Alerts")
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.leftMargin: 983
        anchors.rightMargin: 33
        anchors.topMargin: 157
        anchors.bottomMargin: 803
        font.pixelSize: 80
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        font.bold: true
        font.family: "Tahoma"
    }
}
