# hashguard_frontend_images.py
import threading, time, os, json, subprocess, sys
import PySimpleGUI4 as sg
from PIL import Image, ImageTk
import io
from pathlib import Path
import tkinter.filedialog

# Add backend path for imports
BACKEND_DIR = Path(os.getenv("HASHGUARD_BACKEND_PATH", r"C:\\Users\\jaket\\Dev\\SchoolProjects\\HashGuard\\backend"))
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from backend_helper import ensure_backend_running
from ipc import IPCClient


# Graph/icon sizes
BOX_W, BOX_H = 85, 85        # Graph box size (increased from 80x80)
ICON_SIZE = (70, 70)         # icon size inside the box (increased from 65x65)
_photo_refs = {}     # keep PhotoImage references here so they are not garbage collected
FRAME_W = 170            # frame width (same as your Settings frame)
FRAME_H = 110            # frame height (same as your Settings frame)
left_col_w = FRAME_W // 2
right_col_w = FRAME_W - left_col_w


# ---------- Paths ----------
# Handle PyInstaller bundled paths
if getattr(sys, 'frozen', False):
    # Running as bundled executable
    BUNDLE_DIR = sys._MEIPASS
    HASHGUARD_ROOT = Path(os.path.dirname(sys.executable))
    IMAGE_DIR = os.path.join(BUNDLE_DIR, "frontend", "graphics")
else:
    # Running as script
    HERE = os.path.dirname(os.path.abspath(__file__))
    HASHGUARD_ROOT = Path(HERE).parent  # Root HashGuard folder
    IMAGE_DIR = os.path.join(HERE, "graphics")

START_IMG = os.path.join(IMAGE_DIR, "start_image.png")
STOP_IMG = os.path.join(IMAGE_DIR, "stop_image.png")
ICON_FILE = os.path.join(IMAGE_DIR, "app_icon.ico")

# Debug: print paths to verify
print("IMAGE_DIR:", IMAGE_DIR)
print("START_IMG exists:", os.path.exists(START_IMG))
print("STOP_IMG exists:", os.path.exists(STOP_IMG))

# debug prints (run from integrated terminal so you see these)

# ---------- Configuration ----------
QUARANTINE_DIR = HASHGUARD_ROOT / "quarantine"
LOGS_DIR = HASHGUARD_ROOT / "logs" / "logsText"  # Point to monthly text logs
UI_CONFIG = HASHGUARD_ROOT / "ui_config.json"
POLL_INTERVAL = 1.0

print("Using HASHGUARD_ROOT:", HASHGUARD_ROOT)
print("Using QUARANTINE_DIR:", QUARANTINE_DIR)
print("Using LOGS_DIR:", LOGS_DIR)
print("Using UI_CONFIG:", UI_CONFIG)




os.makedirs(QUARANTINE_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

logs = sorted(p.name for p in LOGS_DIR.iterdir() if p.is_file())
quar = sorted(p.name for p in QUARANTINE_DIR.iterdir() if p.is_file() and not p.name.endswith('.meta.json'))
print("Prepared logs list:", logs)
print("Prepared quarantine list:", quar)
# ---------- Colors / style ----------
BG = "#d62626"
FG = "#000000"
BTN_BG = "#ffffff"
BTN_FG = "#000000"
FRAME_BG = "#ffffff"
LIST_BG = "#ffffff"
LIST_FG = "#000000"

sg.SetOptions(background_color=BG, element_background_color=BG, text_color=FG)

# ---------- Real backend bridge (IPC) ----------
class HashGuardBackend:
    def __init__(self, window):
        self.window = window
        self.client = IPCClient()
        self.connected = False
        self.scanning = False

    def connect(self):
        if self.connected:
            return True
        
        # Try to ensure backend service is running
        print("[Frontend] Checking if backend service is running...")
        if not ensure_backend_running(verbose=True):
            print("[Frontend] Backend service not running, may need to start manually")
            self.window.write_event_value("-SETTINGS-STATUS-", "Service not running")
            return False
        
        print("[Frontend] Backend service is running, connecting...")
        if self.client.connect():
            self.connected = True
            self.window.write_event_value("-SETTINGS-STATUS-", "Connected")
            return True
        self.window.write_event_value("-SETTINGS-STATUS-", "Connect failed")
        return False

    def start_scan(self):
        if not self.connect():
            return
        resp = self.client.send_command({"type": "start_scan"})
        if resp and resp.get("status") == "ok":
            self.scanning = True
            self.window.write_event_value("-BACKEND-STATUS-", "started")

    def stop_scan(self):
        if not self.connected:
            return
        resp = self.client.send_command({"type": "stop_scan"})
        if resp and resp.get("status") == "ok":
            self.scanning = False
            self.window.write_event_value("-BACKEND-STATUS-", "stopped")

    def pause_scan(self):
        if not self.connected:
            return
        self.client.send_command({"type": "pause_scan"})

    def resume_scan(self):
        if not self.connected:
            return
        self.client.send_command({"type": "resume_scan"})

    def set_downloads_folder(self, folder_path):
        if not self.connect():
            return False
        resp = self.client.send_command({"type": "set_watch_path", "path": folder_path})
        if resp and resp.get("status") == "ok":
            self.window.write_event_value("-SETTINGS-STATUS-", f"watching: {folder_path}")
            return True
        # Show popup for failure instead of changing connection status
        import PySimpleGUI4 as sg
        sg.popup("Failed to set watch path", title="Error", background_color="#d62626")
        return False

    def get_status(self):
        if not self.connect():
            return None
        return self.client.send_command({"type": "get_status"})

    def shutdown(self):
        try:
            self.client.close()
        except Exception:
            pass

# ---------- Layout sizes ----------
WINDOW_SIZE = (700, 400)
COLUMN_WIDTH = 340
COLUMN_HEIGHT = 370
icon_path = ICON_FILE if os.path.exists(ICON_FILE) else None

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

def draw_centered_with_pillow(graph_elem, image_path, icon_size, ref_key):
    try:
        img = Image.open(image_path).convert("RGBA")
        img = img.resize(icon_size, Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)

        canvas = graph_elem.TKCanvas
        canvas.update_idletasks()
        cw = canvas.winfo_width()
        ch = canvas.winfo_height()
        cx = cw // 2
        cy = ch // 2

        tag = f"icon_{ref_key}"
        try:
            canvas.delete(tag)
        except Exception:
            pass

        canvas.create_image(cx, cy, image=photo, anchor="center", tags=(tag,))
        _photo_refs[ref_key] = photo
    except Exception as e:
        print("ERROR: draw_centered_with_pillow failed:", e)
    
def clear_icon_tag(graph_elem, ref_key):
    try:
        graph_elem.TKCanvas.delete(f"icon_{ref_key}")
    except Exception:
        pass
def safe_set_start_image():
    """Draw the start image into the Graph only."""
    try:
        clear_icon_tag(graph, "main")
        if os.path.exists(START_IMG):
            draw_centered_with_pillow(graph, START_IMG, ICON_SIZE, "main")
    except Exception:
        pass

def safe_set_stop_image():
    """Draw the stop image into the Graph only."""
    try:
        clear_icon_tag(graph, "main")
        if os.path.exists(STOP_IMG):
            draw_centered_with_pillow(graph, STOP_IMG, ICON_SIZE, "main")
    except Exception:
        pass

# Refresh logic

# ---------- Frames ----------
# Scanner top row: "Scanner" label and status to its right on same line
scanner_column = sg.Column(
    [
        [sg.Text("Scanner",
                 background_color=FRAME_BG,
                 text_color=BTN_FG,
                 font=("Segoe UI", 10, "bold"),
                 pad=(0, 4))],                # small bottom pad
        [sg.Text("", key="-STATUS-",
                 background_color=FRAME_BG,
                 text_color=BTN_FG,
                 font=("Segoe UI", 10, "bold"),
                 size=(8, 1),                 # Fixed width to prevent shifting
                 justification="center",      # Center text within fixed width
                 pad=(0, 0))]                 # no extra padding for alignment
    ],
    background_color=FRAME_BG,
    vertical_alignment="top",                # <-- use top so rows stack at top
    element_justification="center",          # Center align both texts
    size=(75, None),
    pad=(6, 0)
)

start_graph = sg.Graph(
    canvas_size=(BOX_W, BOX_H),
    graph_bottom_left=(0, 0),
    graph_top_right=(BOX_W, BOX_H),
    key="-GRAPH-",
    background_color=FRAME_BG,
    enable_events=True
)

graph_column = sg.Column(
    [[start_graph]],
    background_color=FRAME_BG,
    vertical_alignment="center",
    element_justification="left",
    size=(right_col_w, FRAME_H),
    pad=(0,0)  # Shift left by positioning at edge
)

start_frame = [
    [scanner_column, graph_column]
]

settings_frame = [
    [sg.Text("Settings", background_color=FRAME_BG, text_color=BTN_FG, font=("Segoe UI", 10, "bold"))],
    [sg.Text("", key="-CONNECTION-STATUS-", background_color=FRAME_BG, text_color=BTN_FG, font=("Segoe UI", 9), size=(20, 1))],
    [sg.Button("Downloads", key="-DOWNLOADS-", button_color=(BTN_FG, BTN_BG))],
    [sg.Button("Connect", key="-CONNECT-", button_color=(BTN_FG, BTN_BG))]
]

logs_frame = [
    [sg.Text("Logs", background_color=FRAME_BG, text_color=BTN_FG, font=("Segoe UI", 11, "bold"))],
    [sg.Listbox(values=logs, size=(40,10), key="-LOGS-", enable_events=True,
                background_color=LIST_BG, text_color=LIST_FG)],
    [sg.Button("View Report", key="-OPENLOG-", button_color=(BTN_FG, BTN_BG))]
]

quarantine_frame = [
    [sg.Text("Quarantine", background_color=FRAME_BG, text_color=BTN_FG, font=("Segoe UI", 11, "bold"))],
    [sg.Listbox(values=quar, size=(40,15), key="-QUARANTINE-", enable_events=True,
                background_color=LIST_BG, text_color=LIST_FG)],

    [sg.Button("Delete Selected", key="-DELETE-", button_color=(BTN_FG, BTN_BG))]
]

# Compose left column: two small frames side-by-side on top, logs below
left_column_layout = [
    [sg.Frame("", start_frame, background_color=FRAME_BG, relief=sg.RELIEF_SUNKEN, size=(FRAME_W, FRAME_H)),
     sg.Frame("", settings_frame, background_color=FRAME_BG, relief=sg.RELIEF_SUNKEN, size=(FRAME_W, FRAME_H))],
    [sg.Frame("", logs_frame, background_color=FRAME_BG, relief=sg.RELIEF_SUNKEN, size=(COLUMN_WIDTH, COLUMN_HEIGHT - FRAME_H))]
]


left_column = sg.Column(left_column_layout, background_color=BG, size=(COLUMN_WIDTH, COLUMN_HEIGHT), vertical_alignment='top', pad=(0,0))
right_column = sg.Column([[sg.Frame("", quarantine_frame, background_color=FRAME_BG, relief=sg.RELIEF_SUNKEN, size=(COLUMN_WIDTH, COLUMN_HEIGHT))]],
                         background_color=BG, size=(COLUMN_WIDTH, COLUMN_HEIGHT), vertical_alignment='top', pad=(0,0))

layout = [[left_column, right_column]]

window = sg.Window("HashGuard", layout, finalize=True, background_color=BG, size=WINDOW_SIZE, resizable=False)
graph = window["-GRAPH-"]
# Set the window icon: prefer an .ico if available, otherwise fall back to start image as PhotoImage
try:
    if icon_path:
        window.set_icon(icon_path)
    elif os.path.exists(START_IMG):
        fallback_icon = ImageTk.PhotoImage(Image.open(START_IMG))
        window.TKroot.iconphoto(False, fallback_icon)
        _photo_refs["window_icon"] = fallback_icon  # keep ref alive
except Exception as e:
    print(f"WARNING: failed to set window icon: {e}")
print("Window keys:", sorted(window.AllKeysDict.keys()))
if "-DELETE-" in window.AllKeysDict:
    print("DELETE visible:", window["-DELETE-"].visible, "disabled:", window["-DELETE-"].Disabled)

def set_status(text):
    # update with guaranteed visible color and force redraw
    window["-STATUS-"].update(text, text_color="#000000", background_color=FRAME_BG, visible=True)
    window.refresh()

window.read(timeout=50)
                                # let tkinter do a layout pass
graph.TKCanvas.update_idletasks()
cw = graph.TKCanvas.winfo_width()
ch = graph.TKCanvas.winfo_height()

# draw now if canvas is ready, otherwise defer to event loop
if cw > 1 and ch > 1:
    need_initial_draw = False
else:
    need_initial_draw = True

# Set initial status
set_status("Idle")

# ---------- Start backend bridge ----------
backend = HashGuardBackend(window)

# Initialize connection status and check scanning state
scanning = False
if backend.connect():
    window["-CONNECTION-STATUS-"].update("connected")
    
    # Check if backend is already scanning
    status = backend.get_status()
    if status and status.get("scanning"):
        scanning = True
        set_status("Running")
    else:
        scanning = False
        set_status("Idle")
else:
    window["-CONNECTION-STATUS-"].update("not connected")

# Now draw the correct image based on scanning state
if scanning:
    safe_set_stop_image()
else:
    safe_set_start_image()

# Force canvas to update
try:
    graph.TKCanvas.update_idletasks()
    window.refresh()
except Exception as e:
    print(f"ERROR: Failed to refresh canvas: {e}")

# ---------- Helpers ----------
def request_backend_delete(name):
    def worker(name):
        path = QUARANTINE_DIR / name
        meta = path.with_suffix(path.suffix + ".meta.json")
        try:
            if path.exists():
                path.unlink()
            if meta.exists():
                meta.unlink()
            ok, err = True, ""
        except Exception as e:
            ok, err = False, str(e)
        window.write_event_value("-BACKEND-DELETE-RESULT-", {"name": name, "ok": ok, "err": err})
    threading.Thread(target=worker, args=(name,), daemon=True).start()


def list_dir_names(folder, skip_meta=False):
    try:
        os.makedirs(folder, exist_ok=True)  # Ensure folder exists
        entries = []
        for item in os.listdir(folder):
            if skip_meta and item.endswith(".meta.json"):
                continue
            entries.append(item)
        return sorted(entries)
    except Exception as e:
        print(f"Error listing {folder}: {e}")
        return []

# Cache for list contents to avoid unnecessary refreshes
# Initialize with current state so first refresh doesn't think things changed
_last_logs_list = None
_last_quarantine_list = None

def refresh_lists():
    """Only refresh lists if they've actually changed."""
    global _last_logs_list, _last_quarantine_list
    
    try:
        # Get monthly reports from backend database
        new_logs = []
        if backend.connected:
            try:
                response = backend.client.send_command({"type": "get_monthly_reports"})
                if response and response.get("status") == "ok":
                    new_logs = response.get("months", [])
            except Exception as e:
                print(f"ERROR querying backend for monthly reports: {e}")
                # Fallback to reading files if backend fails
                new_logs = list_dir_names(LOGS_DIR)
        else:
            # Fallback if no IPC connection
            new_logs = list_dir_names(LOGS_DIR)
        
        new_quarantine = list_dir_names(QUARANTINE_DIR, skip_meta=True)
        
        updated = False
        
        # Only update if contents actually changed
        if new_logs != _last_logs_list:
            try:
                # Update logs listbox with direct Tkinter manipulation
                logs_widget = window["-LOGS-"].Widget
                logs_widget.delete(0, 'end')
                for item in new_logs:
                    logs_widget.insert('end', item)
                _last_logs_list = new_logs
                updated = True
            except Exception as e:
                print(f"ERROR updating logs listbox: {e}")
        
        if new_quarantine != _last_quarantine_list:
            try:
                # Update quarantine listbox with direct Tkinter manipulation
                quar_widget = window["-QUARANTINE-"].Widget
                quar_widget.delete(0, 'end')
                for item in new_quarantine:
                    quar_widget.insert('end', item)
                _last_quarantine_list = new_quarantine
                updated = True
            except Exception as e:
                print(f"ERROR updating quarantine listbox: {e}")
        
        # Force window refresh if we updated
        if updated:
            window.refresh()
            
    except Exception as e:
        print(f"ERROR in refresh_lists: {e}")

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

# ---------- Poller ----------
def poller_thread(window, interval):
    while True:
        time.sleep(interval)
        window.write_event_value("-POLL-", None)

poller = threading.Thread(target=poller_thread, args=(window, POLL_INTERVAL), daemon=True)
poller.start()

# Initialize cache variables with what's actually in the listboxes
if backend.connected:
    # Get current logs from backend
    try:
        response = backend.client.send_command({"type": "get_monthly_reports"})
        if response and response.get("status") == "ok":
            _last_logs_list = response.get("months", [])
        else:
            _last_logs_list = []
    except Exception:
        _last_logs_list = []
else:
    _last_logs_list = list_dir_names(LOGS_DIR)

_last_quarantine_list = list_dir_names(QUARANTINE_DIR, skip_meta=True)

# NOTE: Image is already drawn above based on backend scanning state, don't override it here

# ---------- Event loop ----------
scanning = False
# Cache is already initialized above after backend connection
first_loop = True

while True:
    event, values = window.read(timeout=1000)
    
    # On first iteration, populate logs listbox from backend
    if first_loop:
        first_loop = False
        if backend.connected:
            try:
                response = backend.client.send_command({"type": "get_monthly_reports"})
                if response and response.get("status") == "ok":
                    months = response.get("months", [])
                    # Try direct Tkinter manipulation
                    logs_widget = window["-LOGS-"].Widget
                    logs_widget.delete(0, 'end')  # Clear existing
                    for item in months:
                        logs_widget.insert('end', item)  # Add each item
                    _last_logs_list = months
            except Exception:
                pass
        continue

    if need_initial_draw:
        graph.TKCanvas.update_idletasks()
        if graph.TKCanvas.winfo_width() > 1 and graph.TKCanvas.winfo_height() > 1:
            draw_centered_with_pillow(graph, START_IMG, ICON_SIZE, "main")
            need_initial_draw = False
    
    if event == sg.WIN_CLOSED:
        backend.shutdown()
        break
    if event == "-BACKEND-DELETE-RESULT-":
        info = values[event]
        if not info.get("ok"):
            sg.popup(f"Failed to delete {info['name']}:\n{info.get('err')}", title="Delete error")
        refresh_lists()

    if event in ("-POLL-", "-BACKEND-UPDATE-"):
        refresh_lists()

    if event == "-GRAPH-":
        # treat any click inside graph as start/stop
        if not scanning:
            backend.start_scan()
        else:
            backend.stop_scan()

    if event == "-BACKEND-STATUS-":
        status = values[event]
        if status == "started":
            scanning = True
            set_status("Running")
            safe_set_stop_image()
        elif status == "stopped":
            scanning = False
            set_status("Idle")
            safe_set_start_image()

    if event == "-SETTINGS-STATUS-":
        status = values[event]
        window["-CONNECTION-STATUS-"].update(status)

    if event == "-DOWNLOADS-":
        folder = sg.popup_get_folder("Select Downloads Folder", no_window=True)
        if folder:
            # Tell backend to set downloads path
            backend.set_downloads_folder(folder)

    if event == "-CONNECT-":
        backend.connect()

    if event == "-OPENLOG-":
        # Get selection directly from Tkinter widget since we manipulate it directly
        logs_widget = window["-LOGS-"].Widget
        selection = logs_widget.curselection()
        
        if selection:
            index = selection[0]
            month_str = logs_widget.get(index)
            # Query backend for the report
            try:
                response = backend.client.send_command({"type": "get_monthly_report", "month": month_str})
                if response and response.get("status") == "ok":
                    lines = response.get("lines", [])
                    # Display in a custom window with scrollable text
                    report_text = "\n".join(lines) if lines else "(No entries for this month)"
                    
                    # Create a simple popup window with scrollable text
                    layout = [
                        [sg.Multiline(report_text, size=(80, 20), disabled=True, no_scrollbar=False)],
                        [sg.Button("Close")]
                    ]
                    report_window = sg.Window(f"Log Report - {month_str}", layout, background_color=BG)
                    while True:
                        event_r, _ = report_window.read()
                        if event_r == sg.WIN_CLOSED or event_r == "Close":
                            break
                    report_window.close()
                else:
                    sg.popup(f"Error: {response.get('message', 'Unknown error')}", title="Error", background_color=BG)
            except Exception as e:
                sg.popup(f"Error querying backend: {e}", title="Error", background_color=BG)
        else:
            sg.popup("Please select a month from the logs list", title="No Selection", background_color=BG)

    if event == "-DELETE-":
        selected = values.get("-QUARANTINE-") or []
        if len(selected) != 1:
            sg.popup("Please select exactly one file to delete", title="Delete quarantined file")
        else:
            name = selected[0]
            confirm = sg.popup_yes_no(f"Delete '{name}' permanently?", title="Confirm delete")
            if confirm == "Yes":
                request_backend_delete(name)   # non-blocking helper shown below
    
    if event == "-BACKEND-UPDATE-":
        refresh_lists()


window.close()