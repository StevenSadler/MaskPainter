from tkinter import *
from tkinter import Tk, Frame
from tkinter.ttk import Notebook

from src.model.Model import Model
from src.control.MenuBar import MenuBar
from src.control.StatusPanel import StatusPanel
from src.control.BrushControl import BrushControl
from src.control.LayerControl import LayerControl
from src.control.CanvasPainter import CanvasPainter


class TkPaintApp(Frame):
    def __init__(self, master):
        super().__init__()
        self._appTitle = "Layered Mask Painter"
        self.master = master
        self.master.title(self._appTitle)

        # vars used for widget sizes and root geometry
        canvas_width = 640    # 256
        canvas_height = 360   # 256
        control_panel_width = 200

        # model must be initialized before widgets and controllers
        model = Model()
        model.subject.save.attach(self._update_save)
        model.subject.project.attach(self._update_project)
        self.model = model

        # set the widgets
        status_label = Label(self.master, text="status label...", bd=1, relief=SUNKEN, anchor=W)
        canvas = Canvas(self.master, width=canvas_width, height=canvas_height, bg="gray50")

        notebook = Notebook(self.master, width=control_panel_width)
        brush_frame = Frame(notebook)
        layer_frame = Frame(notebook)
        notebook.add(brush_frame, text="Brush")
        notebook.add(layer_frame, text="Layers")

        # pack the widgets
        status_label.pack(side=BOTTOM, fill=X)
        canvas.pack(side=RIGHT)
        notebook.pack(side=LEFT, fill=Y)

        # delegate controllers
        self.menuBar = MenuBar(self.master, model, self)
        self.statusPanel = StatusPanel(status_label, model)
        self.brushControl = BrushControl(brush_frame, model)
        self.layerControl = LayerControl(layer_frame, model)
        self.painter = CanvasPainter(canvas, model)

        # set the geometry of the Tk root
        status_height = 17
        req_buffer = 4
        offset_y = -40
        width = control_panel_width + canvas_width + req_buffer
        height = canvas_height + status_height + req_buffer
        x = (self.master.winfo_screenwidth() - width) // 2
        y = (self.master.winfo_screenheight() - height) // 2 + offset_y
        self.master.minsize(width, height)
        self.master.geometry("{}x{}+{}+{}".format(width, height, x, y))

        # to initialize the views, force a subject project notification
        model.subject.project.notify()

    def _update_save(self):
        if not self.model.isProjectLoaded:
            self.master.title(self._appTitle)
        elif self.model.isCurrentSaved:
            self.master.title("{} - {}".format(self._appTitle, self.model.project.projectFileName))
        else:
            self.master.title("{} - {} *".format(self._appTitle, self.model.project.projectFileName))

    def _update_project(self):
        if not self.model.isProjectLoaded:
            self.master.title(self._appTitle)
        else:
            self.master.title("{} - {}".format(self._appTitle, self.model.project.projectFileName))

    # menu bar click handlers
    def breakpoint_app(self):
        print("breakpoint app", self)


def main():

    root = Tk()
    # root.geometry("800x600+300+100")
    TkPaintApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
