from tkinter import *
from tkinter import simpledialog, colorchooser, messagebox

from src.Utils import Utils


class LayerControl:
    def __init__(self, master, model):
        super().__init__()
        self.master = master
        self.model = model
        self.model.subject.project.attach(self._update_project)

        self._reset()

    def _reset(self):
        self._next_row = 0

    def _update_project(self):
        for widget in self.master.winfo_children():
            widget.grid_forget()
            widget.destroy()
        if self.model.isProjectLoaded:
            self._reset()
            self._add_layer_controls()

    def _add_layer_controls(self):
        def grid_row(*args):
            for c in range(len(args)):
                args[c].grid(row=self._next_row, column=c)
            self._next_row += 1

        label = Label(self.master, text='Edit layers')

        bg_label_button = Button(self.master, width='10', text=self.model.project.layerNames[0],
                                 command=lambda layer=0: self._prompt_layer_name(layer))
        bg_color_button = Button(self.master, width='8', bg=self.model.project.layerColors[0],
                                 command=lambda layer=0: self._prompt_layer_color_chooser(layer))
        bg_hex_button = Button(self.master, width='8', text=self.model.project.layerColors[0],
                               command=lambda layer=0: self._prompt_layer_hex_color(layer))
        bg_add_button = Button(self.master, width='4', text='+^',
                               command=lambda layer=0: self.model.add_layer(layer + 1))

        layer_rows = []
        for mask in range(self.model.project.numMasks):
            layer_button = Button(self.master, width='10', text=self.model.project.layerNames[mask + 1],
                                  command=lambda layer=mask+1: self._prompt_layer_name(layer))
            color_button = Button(self.master, width='8', bg=self.model.project.layerColors[mask + 1],
                                  command=lambda layer=mask+1: self._prompt_layer_color_chooser(layer))
            hex_button = Button(self.master, width='8', text=self.model.project.layerColors[mask + 1],
                                command=lambda layer=mask+1: self._prompt_layer_hex_color(layer))
            add_button = Button(self.master, width='4', text='+^',
                                command=lambda layer=mask+1: self.model.add_layer(layer + 1))

            layer_rows.append((layer_button, color_button, hex_button, add_button))

        # add the layers in the same order as PhotoShop
        # so those at the top will be in the foreground
        # and those at the bottom will be in the background
        # add_label_row(label)
        grid_row(label)
        for i in range(self.model.project.numMasks - 1, -1, -1):
            grid_row(layer_rows[i][0], layer_rows[i][1], layer_rows[i][2], layer_rows[i][3])
        grid_row(bg_label_button, bg_color_button, bg_hex_button, bg_add_button)

    ################################
    #
    #  click handlers
    #
    ################################

    def _prompt_layer_name(self, layer):
        answer = simpledialog.askstring("Change layer name", "Enter new name of layer")
        if answer:
            self.model.set_layer_name(layer, answer)

    def _prompt_layer_color_chooser(self, layer):
        _, answer = colorchooser.askcolor(title="Choose a new layer color")
        if answer:
            self.model.set_layer_color(layer, answer)

    def _prompt_layer_hex_color(self, layer):
        answer = simpledialog.askstring("Choose a new layer color",
                                        "Enter new hex color of layer.\nEnter 3 or 6 hexdigits.")
        if answer:
            if Utils.is_hex_color(answer):
                if answer[0] != '#':
                    answer = "#{}".format(answer)
                self.model.set_layer_color(layer, answer.lower())
            else:
                is_ok = messagebox.askyesno("Invalid entry", "{} is not a valid hex color. Try again?".format(answer))
                if is_ok:
                    self._prompt_layer_hex_color(layer)
