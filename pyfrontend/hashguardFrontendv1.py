# hashguard_frontend_700x400.py
import threading, time, os, json, subprocess, sys
import PySimpleGUI4 as sg   # or import PySimpleGUI as sg

# ---------- Configuration ----------
BASE_DIR = os.path.expanduser(r"~\HashGuardDemo")
QUARANTINE_DIR = os.path.join(BASE_DIR, "quarantine")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
UI_CONFIG = os.path.join(BASE_DIR, "ui_config.json")
POLL_INTERVAL = 1.0

os.makedirs(QUARANTINE_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(BASE_DIR, exist_ok=True)

# ---------- Colors / style ----------
BG = "#d62626"        # window background
FG = "#000000"        # all text black
BTN_BG = "#ffffff"    # button background (white)
BTN_FG = "#000000"    # button text (black)
FRAME_BG = "#ffffff"  # frame background (white)
LIST_BG = "#ffffff"   # listbox background
LIST_FG = "#000000"   # listbox text color
CTRL_BG = "#f2f2f2"   # control panel background (light gray)
CTRL_FG = "#000000"   # control panel text (black)

# Apply general options
sg.SetOptions(background_color=BG, element_background_color=BG, text_color=FG)

# ---------- Mock backend (same behavior as before) ----------
class MockBackend(threading.Thread):
    def __init__(self, window):
        super().__init__(daemon=True)
        self.window = window
        self.running = False
        self._stop = threading.Event()

    def run(self):
        counter = 0
        while not self._stop.is_set():
            if self.running:
                counter += 1
                logname = f"log_{int(time.time())}.txt"
                with open(os.path.join(LOGS_DIR, logname), "w", encoding="utf-8") as f:
                    f.write(f"Mock scan log entry {counter}\n")
                if counter % 3 == 0:
                    qname = f"quarantined_file_{counter}.txt"
                    with open(os.path.join(QUARANTINE_DIR, qname), "w", encoding="utf-8") as f:
                        f.write("This file was quarantined by MockBackend\n")
                self.window.write_event_value("-BACKEND-UPDATE-", "tick")
            time.sleep(2)

    def start_scan(self):
        self.running = True
        self.window.write_event_value("-BACKEND-STATUS-", "started")

    def stop_scan(self):
        self.running = False
        self.window.write_event_value("-BACKEND-STATUS-", "stopped")

    def delete_quarantine(self, filename):
        path = os.path.join(QUARANTINE_DIR, filename)
        try:
            os.remove(path)
            self.window.write_event_value("-BACKEND-UPDATE-", "deleted")
            return True, ""
        except Exception as e:
            return False, str(e)

    def set_config(self, config_path):
        self.window.write_event_value("-BACKEND-STATUS-", f"config_set:{config_path}")

    def shutdown(self):
        self._stop.set()

# ---------- Layout with fixed window size 700x400 ----------
# We calculate listbox sizes to fit the 700x400 window comfortably.
# The frame widths are chosen so left column (controls + logs) and right column (quarantine) align.
WINDOW_SIZE = (700, 400)

# Control panel (distinct look)
control_panel = [
    [sg.Text("Controls", background_color=CTRL_BG, text_color=CTRL_FG, font=("Segoe UI", 11, "bold"))],
    [sg.Text("Status:", background_color=CTRL_BG, text_color=CTRL_FG), sg.Text("idle", key="-STATUS-", background_color=CTRL_BG, text_color=CTRL_FG)],
    [sg.Button("Start Scan", key="-STARTSTOP-", size=(12,1), button_color=(BTN_FG, BTN_BG)),
     sg.Button("Settings", key="-SETTINGS-", button_color=(BTN_FG, BTN_BG))],
    [sg.Text("", background_color=CTRL_BG, size=(1,1))],  # spacer
    [sg.Button("Refresh Lists", key="-REFRESH-", button_color=(BTN_FG, BTN_BG))]
]

# Logs frame (white box)
# size=(40,18) roughly maps to a height that will fit inside 400px window; adjust columns to match visually
logs_frame = [
    [sg.Text("Logs", background_color=FRAME_BG, text_color=BTN_FG, font=("Segoe UI", 11, "bold"))],
    [sg.Listbox(values=[], size=(40,18), key="-LOGS-", enable_events=True, background_color=LIST_BG, text_color=LIST_FG)],
    [sg.Button("Open Log", key="-OPENLOG-", button_color=(BTN_FG, BTN_BG))]
]

# Quarantine frame (white box) — make height match logs by using same listbox height
quarantine_frame = [
    [sg.Text("Quarantine", background_color=FRAME_BG, text_color=BTN_FG, font=("Segoe UI", 11, "bold"))],
    [sg.Listbox(values=[], size=(40,18), key="-QUARANTINE-", enable_events=True, background_color=LIST_BG, text_color=LIST_FG)],
    [sg.Button("Delete Selected", key="-DELETE-", button_color=(BTN_FG, BTN_BG))]
]

# Compose layout: left column is control panel stacked above logs; right column is quarantine frame
left_column = [
    [sg.Frame("", control_panel, background_color=CTRL_BG, relief=sg.RELIEF_RAISED, size=(320, 110))],
    [sg.Frame("", logs_frame, background_color=FRAME_BG, title_color=BTN_FG, relief=sg.RELIEF_SUNKEN, size=(320, 260))]
]

# Right column frame sized to match left column total height (110 + 260 = 370, fits inside 400)
layout = [
    [sg.Column(left_column, background_color=BG, vertical_alignment='top', size=(340, 370)),
     sg.Frame("", quarantine_frame, background_color=FRAME_BG, title_color=BTN_FG, relief=sg.RELIEF_SUNKEN, size=(340, 370))]
]

window = sg.Window("HashGuard Frontend", layout, finalize=True, background_color=BG, size=WINDOW_SIZE, resizable=False)

# ---------- Start mock backend ----------
backend = MockBackend(window)
backend.start()

# ---------- Helpers ----------
def list_dir_names(folder):
    try:
        return sorted(os.listdir(folder))
    except Exception:
        return []

def open_file_with_default_app(path):
    if sys.platform.startswith("win"):
        os.startfile(path)
    elif sys.platform.startswith("darwin"):
        subprocess.run(["open", path])
    else:
        subprocess.run(["xdg-open", path])

def save_ui_config(cfg):
    with open(UI_CONFIG, "w", encoding="utf-8") as f:
        json.dump(cfg, f)

saved_cfg = {}
if os.path.exists(UI_CONFIG):
    try:
        with open(UI_CONFIG, "r", encoding="utf-8") as f:
            saved_cfg = json.load(f)
    except Exception:
        saved_cfg = {}

# initial populate
window["-LOGS-"].update(list_dir_names(LOGS_DIR))
window["-QUARANTINE-"].update(list_dir_names(QUARANTINE_DIR))

# ---------- Poller ----------
def poller_thread(window, interval):
    while True:
        time.sleep(interval)
        window.write_event_value("-POLL-", None)

poller = threading.Thread(target=poller_thread, args=(window, POLL_INTERVAL), daemon=True)
poller.start()

# ---------- Event loop ----------
scanning = False
while True:
    event, values = window.read(timeout=1000)
    if event == sg.WIN_CLOSED:
        backend.shutdown()
        break

    if event in ("-POLL-", "-BACKEND-UPDATE-"):
        window["-LOGS-"].update(list_dir_names(LOGS_DIR))
        window["-QUARANTINE-"].update(list_dir_names(QUARANTINE_DIR))

    if event == "-BACKEND-STATUS-":
        status = values[event]
        if status == "started":
            scanning = True
            window["-STARTSTOP-"].update("Stop Scan")
            window["-STATUS-"].update("scanning")
        elif status == "stopped":
            scanning = False
            window["-STARTSTOP-"].update("Start Scan")
            window["-STATUS-"].update("idle")
        elif status.startswith("config_set:"):
            pass

    if event == "-STARTSTOP-":
        if not scanning:
            backend.start_scan()
        else:
            backend.stop_scan()

    if event == "-SETTINGS-":
        cfg = sg.popup_get_file("Select config.yaml", file_types=(("YAML Files","*.yaml;*.yml"),), no_window=True)
        if cfg:
            saved_cfg["config_path"] = cfg
            save_ui_config(saved_cfg)
            backend.set_config(cfg)

    if event == "-REFRESH-":
        window["-LOGS-"].update(list_dir_names(LOGS_DIR))
        window["-QUARANTINE-"].update(list_dir_names(QUARANTINE_DIR))

    if event == "-OPENLOG-":
        sel = values["-LOGS-"]
        if sel:
            path = os.path.join(LOGS_DIR, sel[0])
            open_file_with_default_app(path)

    if event == "-DELETE-":
        sel = values["-QUARANTINE-"]
        if sel:
            filename = sel[0]
            ok, err = backend.delete_quarantine(filename)
            if ok:
                window["-QUARANTINE-"].update(list_dir_names(QUARANTINE_DIR))

    if event == "-LOGS-" and values["-LOGS-"]:
        path = os.path.join(LOGS_DIR, values["-LOGS-"][0])
        open_file_with_default_app(path)

    if event == "-QUARANTINE-" and values["-QUARANTINE-"]:
        pass

window.close()