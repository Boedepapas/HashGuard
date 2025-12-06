# centered_graph_pillow.py
import os, io
from PIL import Image, ImageTk
import PySimpleGUI4 as sg

HERE = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(HERE, "graphics")
START_IMG = os.path.join(IMAGE_DIR, "start_image.png")
STOP_IMG  = os.path.join(IMAGE_DIR, "stop_image.png")

BG = "#d62626"; FRAME_BG = "#ffffff"
BOX_W, BOX_H = 80, 80
ICON_SIZE = (60, 60)   # change to desired icon size

layout = [
    [sg.Text("Scanner", background_color=FRAME_BG), sg.Text("idle", key="-STATUS-", background_color=FRAME_BG)],
    [sg.Graph(canvas_size=(BOX_W, BOX_H),
              graph_bottom_left=(0, 0),
              graph_top_right=(BOX_W, BOX_H),
              key="-GRAPH-",
              background_color=FRAME_BG,
              enable_events=True)]
]

window = sg.Window("Centered Graph Icon", layout, finalize=True, background_color=BG)
graph = window["-GRAPH-"]

# Keep PhotoImage references here so they are not garbage collected
_photo_refs = {}

# replace existing draw_centered_with_pillow and initial draw/toggle logic with this

def draw_centered_with_pillow(graph_elem, image_path, icon_size, ref_key):
    try:
        # load and resize
        img = Image.open(image_path).convert("RGBA")
        img = img.resize(icon_size, Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)

        # ensure canvas has correct size info
        canvas = graph_elem.TKCanvas
        canvas.update_idletasks()
        cw = canvas.winfo_width()
        ch = canvas.winfo_height()

        # compute center coordinates in canvas pixels
        cx = cw // 2
        cy = ch // 2

        # remove previous image with the same tag, then draw new one with that tag
        tag = f"icon_{ref_key}"
        try:
            canvas.delete(tag)
        except Exception:
            pass
        canvas.create_image(cx, cy, image=photo, anchor="center", tags=(tag,))

        # keep reference so image is not garbage collected
        _photo_refs[ref_key] = photo
    except Exception as e:
        print("DEBUG: draw_centered_with_pillow failed:", e)

# initial draw (use same ref_key for start so toggle replaces it)
if os.path.exists(START_IMG):
    draw_centered_with_pillow(graph, START_IMG, ICON_SIZE, "main")

# event loop: erase only the tag (keeps other drawings intact)
scanning = False
while True:
    event, vals = window.read(timeout=1000)
    if event in (sg.WIN_CLOSED, None):
        break
    if event == "-GRAPH-":
        scanning = not scanning
        window["-STATUS-"].update("scanning" if scanning else "idle")
        # delete the previous icon tag before drawing the new one
        try:
            graph.TKCanvas.delete("icon_main")
        except Exception:
            pass
        img = STOP_IMG if scanning else START_IMG
        if os.path.exists(img):
            draw_centered_with_pillow(graph, img, ICON_SIZE, "main")

window.close()