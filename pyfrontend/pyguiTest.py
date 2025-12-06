import PySimpleGUI4 as sg

layout = [[sg.Text('Hello from PySimpleGUI')]]

window = sg.Window('My First GUI', layout,size=(700,400))

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
window.close()
          
