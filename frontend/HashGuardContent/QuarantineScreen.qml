import QtQuick
import QtQuick.Controls
import HG_quarantine_screen_ui

HG_quarantine_screen_ui {
    id: logsScreen
    anchors.fill: parent
    
    //logic part
    home_page_mouse_area.onClicked: {
        root.currentPage = "HomeScreen.qml"
    }
    settings_page_mouse_area.onClicked: {
        root.currentPage = "SettingsScreen.qml"
    }
    logs_page_mouse_area.onClicked: {
        root.currentPage = "LogsScreen.qml"
    }
    homeScreen.onClicked: {
        root.currentPage = "HomeScreen.qml"
    }
    //quarantine button menu logic
    delete_button_clickable.onClicked: {
        Rectangle {
            id: delete_confirmation_box
            width: 400
            height: 200
            color: "#ffffff"
            radius: 20
            anchors.centerIn: parent

            Text {
                id: delete_confirmation_text
                text: qsTr("Are you sure you want to delete the selected file(s) from quarantine?")
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.topMargin: 20
                font.pixelSize: 20
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                font.family: "Tahoma"
            }

            Row {
                id: confirmation_buttons_row
                spacing: 20
                anchors.bottom: parent.bottom
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.bottomMargin: 20

                Button {
                    id: confirm_delete_button
                    text: qsTr("Yes")
                    onClicked: {
                        //call backend function to delete selected file(s)
                        backend.quarantine.deleteSelectedFile(currentFiles.index)// should be a filepath in txt form
                        delete_confirmation_box.visible = false
                        //refresh the quarantine list
                        currentFiles = backend.quarantineFiles.slice(page * pageSize, (page+1) * pageSize)
                    }
                }

                Button {
                    id: cancel_delete_button
                    text: qsTr("No")
                    onClicked: {
                        delete_confirmation_box.visible = false
                    }
                }
            }
        }
    }
    property int page: 0
    property int pageSize: 7

    // Filtered model for current page
    property var currentFiles: backend.quarantineFiles.slice(page * pageSize, (page+1) * pageSize)

    Column {
        anchors.fill: quarantine_area
        spacing: 10

        Repeater {
            model: currentFiles.length
            delegate: Text {
                text: currentFiles[index]
                visible: currentFiles.length > 0
            }
        }
        Row {
            spacing: 20
            Button {
                text: "Previous"
                enabled: page > 0
                onClicked: page--
            }
            Button {
                text: "Next"
                enabled: (page+1) * pageSize < backend.quarantineFiles.length
                onClicked: page++
            }
        }
    }
}