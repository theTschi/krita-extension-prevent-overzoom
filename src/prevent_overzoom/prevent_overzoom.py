from krita import Krita, Extension
from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QMdiArea

ACTION_NAME = "prevent_overzoom"
ACTION_TITLE = "Prevent overzoom"
MAX_ZOOM = 1.0
DEFAULT_DPI = 72
ZOOM_LEVEL_DIGITS = 3
ZOOM_LEVELS = [[0.0, 0.021], 
               [0.021, 0.031],
               [0.031, 0.042],
               [0.042, 0.063],
               [0.063, 0.083],
               [0.083, 0.125],
               [0.125, 0.167],
               [0.167, 0.25], 
               [0.25 ,0.333],
               [0.333, 0.5],
               [0.5, 0.667], 
               [0.667, 1.0]]
MIN = 0
MAX = 1

g_shortcut_pressed = False

class mdiArea(QMdiArea):
    def __init__(self, parent=None):
        super().__init__(parent)

    def resolution_factor(self) -> float:
        resolution = Krita.instance().activeDocument().resolution()
        resolution_factor = resolution / DEFAULT_DPI
        return resolution_factor

    def new_zoom_level(self, current_zoom_level) -> float:
        current_zoom = round(current_zoom_level, ZOOM_LEVEL_DIGITS)
        for zoom_level in ZOOM_LEVELS:
            if (current_zoom >= zoom_level[MIN]) and (current_zoom < zoom_level[MAX]):
                return zoom_level[MAX]

    def zoom_in(self):
        canvas = Krita.instance().activeWindow().activeView().canvas()
        current_zoom_level = canvas.zoomLevel() / self.resolution_factor()
        if current_zoom_level >= MAX_ZOOM:
            new_zoom_level = MAX_ZOOM
        else:
            new_zoom_level = self.new_zoom_level(current_zoom_level)
        canvas.setZoomLevel(new_zoom_level)

    def eventFilter(self, obj, e):
        global g_shortcut_pressed
        if ((e.type() == QEvent.KeyRelease) and (g_shortcut_pressed)):
            g_shortcut_pressed = False
            self.zoom_in()
        return False

class PreventOverzoomExtension(Extension):
    def __init__(self,parent):
        super(PreventOverzoomExtension, self).__init__(parent)

    def setup(self):
        pass

    def trigger(self):
        global g_shortcut_pressed
        g_shortcut_pressed = True

    def createActions(self, window):
        self.c_prevent_overzoom = window.createAction(ACTION_NAME, ACTION_TITLE)
        self.c_prevent_overzoom.triggered.connect(self.trigger)
        self.c_prevent_overzoom.setAutoRepeat(False)
        self.mdiArea = mdiArea()

def register_extension():
    krita_app = Krita.instance()
    prevent_overzoom_extension = PreventOverzoomExtension(krita_app)
    krita_app.addExtension(prevent_overzoom_extension)

register_extension()
