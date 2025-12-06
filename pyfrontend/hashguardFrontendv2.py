# hashguard_frontend_images.py
import threading, time, os, json, subprocess, sys
import PySimpleGUI4 as sg

# ---------- Paths ----------
HERE = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR  = os.path.join(HERE, "graphics")
START_IMG = os.path.join(IMAGE_DIR, "start_image.png")
STOP_IMG = os.path.join(IMAGE_DIR, "stop_image.png")

# debug prints (run from integrated terminal so you see these)
print("DEBUG: script folder:", HERE)
print("DEBUG: image folder:", IMAGE_DIR)
print("DEBUG: start exists:", os.path.exists(START_IMG))
print("DEBUG: stop exists: ", os.path.exists(STOP_IMG))

# ---------- Configuration ----------
BASE_DIR = os.path.expanduser(r"~\\HashGuardDemo")
QUARANTINE_DIR = os.path.join(BASE_DIR, "quarantine")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
UI_CONFIG = os.path.join(BASE_DIR, "ui_config.json")
POLL_INTERVAL = 1.0

os.makedirs(QUARANTINE_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(BASE_DIR, exist_ok=True)

# ---------- Colors / style ----------
BG = "#d62626"
FG = "#000000"
BTN_BG = "#ffffff"
BTN_FG = "#000000"
FRAME_BG = "#ffffff"
LIST_BG = "#ffffff"
LIST_FG = "#000000"

sg.SetOptions(background_color=BG, element_background_color=BG, text_color=FG)

# ---------- Mock backend (for testing) ----------
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
                # create a log file
                logname = f"log_{int(time.time())}.txt"
                with open(os.path.join(LOGS_DIR, logname), "w", encoding="utf-8") as f:
                    f.write(f"Mock scan log entry {counter}\n")
                # occasionally quarantine a fake file
                if counter % 3 == 0:
                    qname = f"quarantined_file_{counter}.txt"
                    with open(os.path.join(QUARANTINE_DIR, qname), "w", encoding="utf-8") as f:
                        f.write("This file was quarantined by MockBackend\n")
                # notify UI to refresh lists
                self.window.write_event_value("-BACKEND-UPDATE-", "tick")
            time.sleep(2)

    def start_scan(self):
        if not self.running:
            self.running = True
            self.window.write_event_value("-BACKEND-STATUS-", "started")

    def stop_scan(self):
        if self.running:
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

# ---------- Layout sizes ----------
WINDOW_SIZE = (700, 400)
COLUMN_WIDTH = 340
COLUMN_HEIGHT = 370

# ---------- Helper to create an image button or fallback to text button ----------
def make_image_button(key, image_path, fallback_text, button_size=(40, 40)):
    """
    Returns a PySimpleGUI element: an image button if image exists, otherwise a text button.
    """
    if os.path.exists(image_path):
        try:
            return sg.Button("", key=key, image_filename=image_path, border_width=0, button_color=(BTN_FG, BTN_BG))
        except Exception:
            # fallback to text button if image load fails
            return sg.Button(fallback_text, key=key, button_color=(BTN_FG, BTN_BG))
    else:
        return sg.Button(fallback_text, key=key, button_color=(BTN_FG, BTN_BG))

# ---------- Frames ----------
# Scanner top row: "Scanner" label and status to its right on same line
scanner_header = [sg.Text("Scanner", background_color=FRAME_BG, text_color=BTN_FG, font=("Segoe UI", 10, "bold")),
                  sg.Text("", key="-STATUS-", background_color=FRAME_BG, text_color=BTN_FG, pad=((10,0),0))]

# Image button (start/stop) - initial image will be start_image if present
start_button_element = make_image_button("-START-", START_IMG, "Start Scan")

start_frame = [
    [sg.Column([scanner_header], background_color=FRAME_BG, pad=(0,0))],
    [sg.Column([[start_button_element]], background_color=FRAME_BG, pad=(0,0))]
]

settings_frame = [
    [sg.Text("Settings", background_color=FRAME_BG, text_color=BTN_FG, font=("Segoe UI", 10, "bold"))],
    [sg.Text("Config:", background_color=FRAME_BG, text_color=BTN_FG),
     sg.Text("", key="-CFGNAME-", background_color=FRAME_BG, text_color=BTN_FG)],
    [sg.Button("Choose Config", key="-SETTINGS-", button_color=(BTN_FG, BTN_BG))]
]

logs_frame = [
    [sg.Text("Logs", background_color=FRAME_BG, text_color=BTN_FG, font=("Segoe UI", 11, "bold"))],
    [sg.Listbox(values=[], size=(40,18), key="-LOGS-", enable_events=True, background_color=LIST_BG, text_color=LIST_FG)],
    [sg.Button("Open Log", key="-OPENLOG-", button_color=(BTN_FG, BTN_BG))]
]

quarantine_frame = [
    [sg.Text("Quarantine", background_color=FRAME_BG, text_color=BTN_FG, font=("Segoe UI", 11, "bold"))],
    [sg.Listbox(values=[], size=(40,22), key="-QUARANTINE-", enable_events=True, background_color=LIST_BG, text_color=LIST_FG)],
    [sg.Button("Delete Selected", key="-DELETE-", button_color=(BTN_FG, BTN_BG))]
]

# Compose left column: two small frames side-by-side on top, logs below
left_column_layout = [
    [sg.Frame("", start_frame, background_color=FRAME_BG, relief=sg.RELIEF_SUNKEN, size=(170, 110)),
     sg.Frame("", settings_frame, background_color=FRAME_BG, relief=sg.RELIEF_SUNKEN, size=(170, 110))],
    [sg.Frame("", logs_frame, background_color=FRAME_BG, relief=sg.RELIEF_SUNKEN, size=(COLUMN_WIDTH, COLUMN_HEIGHT - 110))]
]

left_column = sg.Column(left_column_layout, background_color=BG, size=(COLUMN_WIDTH, COLUMN_HEIGHT), vertical_alignment='top', pad=(0,0))
right_column = sg.Column([[sg.Frame("", quarantine_frame, background_color=FRAME_BG, relief=sg.RELIEF_SUNKEN, size=(COLUMN_WIDTH, COLUMN_HEIGHT))]],
                         background_color=BG, size=(COLUMN_WIDTH, COLUMN_HEIGHT), vertical_alignment='top', pad=(0,0))

layout = [[left_column, right_column]]

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

# show saved config name if present
saved_cfg = {}
if os.path.exists(UI_CONFIG):
    try:
        with open(UI_CONFIG, "r", encoding="utf-8") as f:
            saved_cfg = json.load(f)
    except Exception:
        saved_cfg = {}

if saved_cfg.get("config_path"):
    window["-CFGNAME-"].update(os.path.basename(saved_cfg["config_path"]))

window["-LOGS-"].update(list_dir_names(LOGS_DIR))
window["-QUARANTINE-"].update(list_dir_names(QUARANTINE_DIR))

# ---------- Poller ----------
def poller_thread(window, interval):
    while True:
        time.sleep(interval)
        window.write_event_value("-POLL-", None)

poller = threading.Thread(target=poller_thread, args=(window, POLL_INTERVAL), daemon=True)
poller.start()

# ---------- State helpers for image toggle ----------
def set_start_image():
    if os.path.exists(START_IMG):
        try:
            window["-START-"].update(image_filename=START_IMG, text="")
        except Exception:
            window["-START-"].update("Start Scan")
    else:
        window["-START-"].update("Start Scan")

def set_stop_image():
    if os.path.exists(STOP_IMG):
        try:
            window["-START-"].update(image_filename=STOP_IMG, text="")
        except Exception:
            window["-START-"].update("Stop Scan")
    else:
        window["-START-"].update("Stop Scan")

# initialize start button image (in case fallback created a text button earlier)
set_start_image()

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
            window["-STATUS-"].update("scanning")
            set_stop_image()
        elif status == "stopped":
            scanning = False
            window["-STATUS-"].update("idle")
            set_start_image()
        elif status.startswith("config_set:"):
            cfgpath = status.split(":",1)[1]
            window["-CFGNAME-"].update(os.path.basename(cfgpath))

    if event == "-START-":
        # toggle behavior: if currently scanning, stop; otherwise start
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
            window["-CFGNAME-"].update(os.path.basename(cfg))

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