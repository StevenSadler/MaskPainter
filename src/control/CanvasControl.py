class CanvasControl:
    def __init__(self, canvas, model, painter):
        self.canvas = canvas
        self.model = model
        self.model.subject.project.attach(self._update_project)
        self.painter = painter

    def _update_project(self):
        if self.model.isProjectLoaded:
            self._bind()
        else:
            self._unbind()

    def _bind(self):
        # left mouse button to paint
        self.canvas.bind('<Button-1>', self.painter.paint)
        self.canvas.bind('<B1-Motion>', self.painter.paint)
        self.canvas.bind('<ButtonRelease-1>', self.painter.end_brush_stroke)

        # middle mouse button to pan
        self.canvas.bind('<Button-2>', self.painter.pan)
        self.canvas.bind('<B2-Motion>', self.painter.pan)
        self.canvas.bind('<ButtonRelease-2>', self.painter.end_pan)

        # right mouse button to erase
        self.canvas.bind('<Button-3>', self.painter.erase)
        self.canvas.bind('<B3-Motion>', self.painter.erase)
        self.canvas.bind('<ButtonRelease-3>', self.painter.end_brush_stroke)

        # any mouse motion to draw black outline circle
        self.canvas.bind('<Motion>', self._mouse_move)
        self.canvas.bind('<Leave>', self._mouse_exit)

        # mousewheel to zoom
        self.canvas.bind('<MouseWheel>', self.painter.zoom)

        # resize
        self.canvas.bind('<Configure>', self.painter.resize)

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

        # mousewheel to zoom
        self.canvas.unbind('<MouseWheel>')

        # resize
        self.canvas.unbind('<Configure>')

    def _mouse_move(self, e):
        self.painter.render_canvas_image()
        self.painter.render_brush_outline(e.x, e.y)

    def _mouse_exit(self, _):
        self.painter.render_canvas_image()
