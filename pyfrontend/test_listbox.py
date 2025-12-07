#!/usr/bin/env python3
"""Test listbox update functionality."""
import sys
from pathlib import Path

# Add backend path for imports
BACKEND_DIR = Path(__file__).parent.parent / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import PySimpleGUI4 as sg

# Simple test window with listbox
sg.SetOptions(background_color="red", element_background_color="red", text_color="black")

layout = [
    [sg.Text("Test Listbox", font=("Arial", 12, "bold"), background_color="white", text_color="black")],
    [sg.Listbox(values=["item1", "item2", "item3"], size=(40, 10), key="-LIST-", 
                background_color="white", text_color="black")],
    [sg.Button("Update List", key="-UPDATE-"), sg.Button("Exit", key="-EXIT-")]
]

window = sg.Window("Listbox Test", layout, finalize=True, background_color="red", size=(300, 300))

counter = 0
while True:
    event, values = window.read(timeout=1000)
    
    if event == sg.WIN_CLOSED or event == "-EXIT-":
        break
    
    if event == "-UPDATE-":
        counter += 1
        new_list = [f"item{i}" for i in range(1, 4 + counter)]
        print(f"Updating list to: {new_list}")
        try:
            window["-LIST-"].update(values=new_list)
            print("Update successful")
        except Exception as e:
            print(f"ERROR: {e}")
    
    # Auto-update every 3 seconds
    if event == "-TIMEOUT-" or event == sg.TIMEOUT_KEY:
        if counter > 0:
            counter += 1
            if counter > 5:
                counter = 0
            new_list = [f"item{i}" for i in range(1, 4 + counter)]
            try:
                window["-LIST-"].update(values=new_list)
            except Exception as e:
                print(f"ERROR in auto-update: {e}")

window.close()
print("Test complete")
