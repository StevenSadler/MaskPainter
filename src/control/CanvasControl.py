from tkinter import messagebox
import math


class CanvasControl:
    def __init__(self, canvas, model, painter):
        self.canvas = canvas
        self.model = model
        self.model.subject.load.attach(self._update_load)
        self.painter = painter

    def _update_load(self):
        if self.model.isProjectLoaded:
            canvas_size = (self.canvas.winfo_width(), self.canvas.winfo_height())
            self.model.canvas.load(self.model.project.imgSize, canvas_size)
            self._bind()
        else:
            self.model.canvas.reset()
            self._unbind()

    def _bind(self):
        # left mouse button to paint
        self.canvas.bind('<Button-1>', self._start_paint)
        self.canvas.bind('<B1-Motion>', self.painter.paint)
        self.canvas.bind('<ButtonRelease-1>', self._end_brush_stroke)

        # middle mouse button to pan
        self.canvas.bind('<Button-2>', self._start_pan)
        self.canvas.bind('<B2-Motion>', self.painter.pan)
        self.canvas.bind('<ButtonRelease-2>', self._end_pan)

        # right mouse button to erase
        self.canvas.bind('<Button-3>', self._start_erase)
        self.canvas.bind('<B3-Motion>', self.painter.erase)
        self.canvas.bind('<ButtonRelease-3>', self._end_brush_stroke)

        # any mouse motion to draw black outline circle
        self.canvas.bind('<Motion>', self._mouse_move)
        self.canvas.bind('<Leave>', self._mouse_exit)

        # resize
        self.canvas.bind('<Configure>', self._resize)

        self._bind_zoom()

    def _unbind(self):
        # left mouse button to paint
        self.canvas.unbind('<Button-1>')
        self.canvas.unbind('<B1-Motion>')
        self.canvas.unbind('<ButtonRelease-1>')

        # middle mouse button to pan
        self.canvas.unbind('<Button-2>')
        self.canvas.unbind('<B2-Motion>')
        self.canvas.unbind('<ButtonRelease-2>')

        # right mouse button to erase
        self.canvas.unbind('<Button-3>')
        self.canvas.unbind('<B3-Motion>')
        self.canvas.unbind('<ButtonRelease-3>')

        # any mouse motion to draw black outline circle
        self.canvas.unbind('<Motion>')
        self.canvas.unbind('<Leave>')

        # resize
        self.canvas.unbind('<Configure>')

        self._unbind_zoom()

    def _bind_zoom(self):
        self.canvas.bind('<MouseWheel>', self._zoom)

    def _unbind_zoom(self):
        self.canvas.unbind('<MouseWheel>')

    def _zoom(self, e):
        if e.delta > 0 and self.model.canvas.zoom < self.model.canvas.max_zoom:
            # zoom in
            self.model.zoom(self.model.canvas.zoom * 2)
            self.painter.zoom(e)
        elif e.delta < 0 and self.model.canvas.zoom > self.model.canvas.min_zoom:
            # zoom out
            self.model.zoom(int(math.ceil(self.model.canvas.zoom / 2)))
            self.painter.zoom(e)

    def _start_paint(self, e):
        if self.model.project.visibility[self.model.project.activeMask]:
            self._unbind_zoom()
            self.painter.paint(e)
        else:
            self._prompt_show_active_layer()

    def _start_erase(self, e):
        if self.model.project.visibility[self.model.project.activeMask]:
            self._unbind_zoom()
            self.painter.erase(e)
        else:
            self._prompt_show_active_layer()

    def _start_pan(self, e):
        self._unbind_zoom()
        self.painter.pan(e)

    def _end_brush_stroke(self, e):
        self._bind_zoom()
        self.painter.end_brush_stroke(e)

    def _end_pan(self, e):
        self._bind_zoom()
        self.painter.end_pan(e)

    def _mouse_move(self, e):
        self.painter.render_canvas_image()
        self.painter.render_brush_outline(e.x, e.y)

    def _mouse_exit(self, _):
        self.painter.render_canvas_image()

    def _resize(self, e):
        if self.model.isProjectLoaded:
            canvas_size = (e.width, e.height)
            self.model.canvas.resize_canvas(canvas_size)
            self.painter.resize()

    def _prompt_show_active_layer(self):
        layer_name = self.model.project.layerNames[self.model.project.activeMask]
        message = "The active layer {} is hidden. Do you wish to make it visible to allow painting?".format(
            layer_name)
        is_ok = messagebox.askyesno(title="Confirm", message=message, icon="warning")

        if is_ok:
            self.model.toggle_layer_visibility(self.model.project.activeMask)
