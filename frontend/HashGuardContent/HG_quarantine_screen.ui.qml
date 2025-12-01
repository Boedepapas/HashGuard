

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
                    id: homepage_mouse_area
                    anchors.fill: parent
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
                    x: -296
                    y: 0
                    anchors.fill: parent
                }
            }

            Rectangle {
                id: quarantinepagebuttonImage
                color: "#c1c0c0"
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
                    x: -592
                    y: 0
                    anchors.fill: parent
                }
            }
        }
    }

    Rectangle {
        id: quarantine_area
        color: "#e8e7e7"
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.leftMargin: 45
        anchors.rightMargin: 511
        anchors.topMargin: 312
        anchors.bottomMargin: 105

        Rectangle {
            id: quarantine_file1
            x: 43
            y: 49
            visible: true
            color: "#ffffff"
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.leftMargin: 43
            anchors.rightMargin: 43
            anchors.topMargin: 49
            anchors.bottomMargin: 551

            Text {
                id: file1_text
                text: qsTr("Text")
                anchors.fill: parent
                font.pixelSize: 20
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                fontSizeMode: Text.Fit
                font.family: "Tahoma"
            }

            MouseArea {
                id: file1_mouse_area
                x: -43
                y: -49
                anchors.fill: parent
            }
        }

        Rectangle {
            id: quarantine_file2
            x: 43
            y: 137
            visible: true
            color: "#ffffff"
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.leftMargin: 43
            anchors.rightMargin: 43
            anchors.topMargin: 137
            anchors.bottomMargin: 463

            Text {
                id: file2_text
                x: -43
                y: -137
                text: qsTr("Text")
                anchors.fill: parent
                font.pixelSize: 20
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                fontSizeMode: Text.Fit
                font.family: "Tahoma"
            }

            MouseArea {
                id: file2_mouse_area
                x: 0
                y: -88
                anchors.fill: parent
            }
        }

        Rectangle {
            id: quarantine_file3
            x: 43
            y: 223
            visible: true
            color: "#ffffff"
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.leftMargin: 43
            anchors.rightMargin: 43
            anchors.topMargin: 223
            anchors.bottomMargin: 377

            Text {
                id: file3_text
                x: 0
                y: -86
                text: qsTr("Text")
                anchors.fill: parent
                font.pixelSize: 20
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                fontSizeMode: Text.Fit
                font.family: "Tahoma"
            }

            MouseArea {
                id: file3_mouse_area
                x: 0
                y: -86
                anchors.fill: parent
            }
        }

        Rectangle {
            id: quarantine_file4
            x: 43
            y: 307
            visible: true
            color: "#ffffff"
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.leftMargin: 43
            anchors.rightMargin: 43
            anchors.topMargin: 307
            anchors.bottomMargin: 293

            Text {
                id: file4_text
                x: -43
                y: -307
                text: qsTr("Text")
                anchors.fill: parent
                font.pixelSize: 20
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                fontSizeMode: Text.Fit
                font.family: "Tahoma"
            }

            MouseArea {
                id: file4_mouse_area
                x: -43
                y: -307
                anchors.fill: parent
            }
        }

        Rectangle {
            id: quarantine_file5
            x: 43
            y: 392
            visible: true
            color: "#ffffff"
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.leftMargin: 43
            anchors.rightMargin: 43
            anchors.topMargin: 392
            anchors.bottomMargin: 208

            Text {
                id: file5_text
                x: 0
                y: -85
                text: qsTr("Text")
                anchors.fill: parent
                font.pixelSize: 20
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                fontSizeMode: Text.Fit
                font.family: "Tahoma"
            }

            MouseArea {
                id: file5_mouse_area
                x: 0
                y: -85
                anchors.fill: parent
            }
        }

        Rectangle {
            id: quarantine_file6
            x: -2
            y: 161
            visible: true
            color: "#ffffff"
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.leftMargin: 43
            anchors.rightMargin: 43
            anchors.topMargin: 473
            anchors.bottomMargin: 127

            Text {
                id: file6_text
                x: 0
                y: 85
                text: qsTr("Text")
                anchors.fill: parent
                font.pixelSize: 20
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                fontSizeMode: Text.Fit
                font.family: "Tahoma"
            }

            MouseArea {
                id: file6_mouse_area
                x: 0
                y: -81
                anchors.fill: parent
            }
        }

        Rectangle {
            id: quarantine_file7
            x: 43
            y: 558
            visible: true
            color: "#ffffff"
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.leftMargin: 43
            anchors.rightMargin: 43
            anchors.topMargin: 558
            anchors.bottomMargin: 42

            Text {
                id: file7_text
                x: 0
                y: -85
                text: qsTr("Text")
                anchors.fill: parent
                font.pixelSize: 20
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                fontSizeMode: Text.Fit
                font.family: "Tahoma"
            }

            MouseArea {
                id: file7_mouse_area
                x: 0
                y: -85
                anchors.fill: parent
            }
        }
    }

    Text {
        id: quarantine_text
        text: qsTr("Quarantined Files")
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.leftMargin: 421
        anchors.rightMargin: 887
        anchors.topMargin: 170
        anchors.bottomMargin: 792
        font.pixelSize: 57
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        font.family: "Tahoma"
        font.styleName: "Bold"
    }

    Rectangle {
        id: quarantine_button_page
        opacity: 1
        visible: false
        color: "#e8e7e7"
        radius: 40
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.leftMargin: 1454
        anchors.rightMargin: 37
        anchors.topMargin: 312
        anchors.bottomMargin: 63

        Rectangle {
            id: delete_button
            visible: true
            color: "#e8e7e7"
            radius: 40
            border.width: 1
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.leftMargin: 35
            anchors.rightMargin: 35
            anchors.topMargin: 34
            anchors.bottomMargin: 575

            Text {
                id: delete_text
                color: "#f90a0a"
                text: qsTr("Delete File")
                anchors.fill: parent
                font.pixelSize: 50
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                font.styleName: "Bold"
                font.family: "Tahoma"
            }

            Button {
                id: delete_button_clickable
                visible: false
                text: qsTr("Button")
                anchors.fill: parent
            }
        }

        Rectangle {
            id: unquarantine_button
            color: "#e8e7e7"
            radius: 40
            border.width: 1
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.leftMargin: 35
            anchors.rightMargin: 35
            anchors.topMargin: 169
            anchors.bottomMargin: 440

            Text {
                id: unquarantine_text
                color: "#20c00a"
                text: qsTr("Un-Quarantine")
                anchors.fill: parent
                font.pixelSize: 45
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                font.styleName: "Bold"
                font.family: "Tahoma"
            }

            Button {
                id: unquarantine_button_clickable
                visible: false
                text: qsTr("Button")
                anchors.fill: parent
            }
        }

        Rectangle {
            id: inspect_button
            color: "#e8e7e7"
            radius: 40
            border.width: 1
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.leftMargin: 35
            anchors.rightMargin: 35
            anchors.topMargin: 305
            anchors.bottomMargin: 304

            Text {
                id: inspect_text
                text: qsTr("Inspect")
                anchors.fill: parent
                font.pixelSize: 50
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                font.family: "Tahoma"
                font.styleName: "Bold"
            }

            Button {
                id: inspect_button_clickable
                visible: false
                text: qsTr("Button")
                anchors.fill: parent
            }
        }

        Rectangle {
            id: recheck_button
            color: "#e8e7e7"
            radius: 40
            border.width: 1
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.leftMargin: 35
            anchors.rightMargin: 35
            anchors.topMargin: 440
            anchors.bottomMargin: 169

            Text {
                id: recheck_text
                text: qsTr("Recheck")
                anchors.fill: parent
                font.pixelSize: 50
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                font.styleName: "Bold"
                font.family: "Tahoma"
            }

            Button {
                id: recheck_button_clickable
                visible: false
                text: qsTr("Button")
                anchors.fill: parent
            }
        }

        Rectangle {
            id: page_turner
            visible: true
            color: "#e8e7e7"
            radius: 40
            border.width: 1
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.leftMargin: 35
            anchors.rightMargin: 35
            anchors.topMargin: 568
            anchors.bottomMargin: 41
            Text {
                id: page_tuner_text
                color: "#000000"
                text: qsTr("<   Page   >")
                anchors.fill: parent
                font.pixelSize: 50
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                font.styleName: "Bold"
                font.family: "Tahoma"
            }

            Button {
                id: page_turner_back_button
                visible: false
                text: qsTr("Button")
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.leftMargin: 8
                anchors.rightMargin: 251
                anchors.topMargin: 0
                anchors.bottomMargin: 0
            }

            Button {
                id: page_turner_forward_button
                visible: false
                text: qsTr("Button")
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.leftMargin: 255
                anchors.rightMargin: 4
                anchors.topMargin: 0
                anchors.bottomMargin: 0
            }
        }
    }
}
