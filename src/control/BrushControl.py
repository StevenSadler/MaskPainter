from tkinter import *


class BrushControl:
    def __init__(self, master, model):
        super().__init__()
        self.master = master
        self.model = model
        self.model.subject.layer.attach(self._update_layer)
        self.model.subject.project.attach(self._update_project)

        self._reset()

    def _reset(self):
        self._next_row = 0
        self._active_indicators = []
        self._viz_boxes = []

    def _update_layer(self):
        for i in range(self.model.project.numMasks):
            if self.model.activeLayer == i:
                self._active_indicators[i].config(text='Active')
            else:
                self._active_indicators[i].config(text='')

            if self.model.layerVisibility[i]:
                self._viz_boxes[i].select()
            else:
                self._viz_boxes[i].deselect()

    def _update_project(self):
        for widget in self.master.winfo_children():
            widget.grid_forget()
            widget.destroy()
        if self.model.isProjectLoaded:
            self._reset()
            self._add_brush_slider()
            self._add_active_layer_controls()

            # initialize active indicators and viz boxes
            self._update_layer()

    def _add_brush_slider(self):
        Label(self.master, text='Brush Radius').grid(row=self._next_row, column=0)
        slider = Scale(self.master, from_=self.model.brushSizeMin, to=self.model.brushSizeMax,
                       command=self.model.set_brush_size, orient=HORIZONTAL, length=50)
        slider.set(self.model.brushSize)
        slider.grid(row=self._next_row, column=1, columnspan=3, ipadx=30)
        self._next_row += 1

    def _add_active_layer_controls(self):
        def grid_row(*args):
            for c in range(len(args)):
                args[c].grid(row=self._next_row, column=c)
            self._next_row += 1

        label = Label(self.master, text='Active Layer')

        bg_label = Label(self.master, width='10', text=self.model.project.layerNames[0])
        bg_color_button = Button(self.master, width='8', bg=self.model.project.layerColors[0], state=DISABLED)

        layer_rows = []
        for mask in range(self.model.project.numMasks):
            layer_label = Label(self.master, width='10', text=self.model.project.layerNames[mask + 1])
            color_button = Button(self.master, width='8', bg=self.model.project.layerColors[mask + 1],
                                  command=lambda layer=mask: self.model.set_active_layer(layer))
            layer_viz = Checkbutton(self.master, text='show',
                                    command=lambda layer=mask: self.model.toggle_layer_visibility(layer))
            layer_rows.append((layer_label, color_button, layer_viz))

            self._active_indicators.append(color_button)
            self._viz_boxes.append(layer_viz)

        # add the layers in the same order as PhotoShop
        # so those at the top will be in the foreground
        # and those at the bottom will be in the background
        grid_row(label)
        for i in range(self.model.project.numMasks - 1, -1, -1):
            grid_row(layer_rows[i][0], layer_rows[i][1], layer_rows[i][2])
        grid_row(bg_label, bg_color_button)
