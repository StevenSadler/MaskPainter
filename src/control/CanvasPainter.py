from tkinter import *
from tkinter import messagebox
from PIL import ImageTk, Image
import cv2 as cv


class CanvasPainter:
    def __init__(self, canvas, model):
        self.canvas = canvas
        self.model = model
        self.model.subject.layer.attach(self._update_layer)
        self.model.subject.project.attach(self._update_project)
        self.model.subject.export.attach(self._update_export)

        self._bg_image = None
        self._fg_image = None
        self._brush_position = None
        self._color_paint = 'white'
        self._color_erase = 'black'

    def _bind(self):
        # left mouse button to paint
        self.canvas.bind('<Button-1>', self._paint)
        self.canvas.bind('<B1-Motion>', self._paint)
        self.canvas.bind('<ButtonRelease-1>', self._end_brush_stroke)

        # right mouse button to erase
        self.canvas.bind('<Button-3>', self._erase)
        self.canvas.bind('<B3-Motion>', self._erase)
        self.canvas.bind('<ButtonRelease-3>', self._end_brush_stroke)

        # any mouse motion to draw black outline circle
        self.canvas.bind('<Motion>', self._mouse_move)
        self.canvas.bind('<Leave>', self._mouse_exit)

    def _unbind(self):
        # left mouse button to paint
        self.canvas.unbind('<Button-1>')
        self.canvas.unbind('<B1-Motion>')
        self.canvas.unbind('<ButtonRelease-1>')

        # right mouse button to erase
        self.canvas.unbind('<Button-3>')
        self.canvas.unbind('<B3-Motion>')
        self.canvas.unbind('<ButtonRelease-3>')

        # any mouse motion to draw black outline circle
        self.canvas.unbind('<Motion>')
        self.canvas.unbind('<Leave>')

    def _update_layer(self):
        self._bg_image = self._comp_bg_image()
        self._fg_image = self._comp_fg_image()
        self._build_canvas_image()

    def _update_project(self):
        self.canvas.delete(ALL)
        if self.model.isProjectLoaded:
            self._bind()
            self._update_layer()
        else:
            self._unbind()

    def _update_export(self):
        temp_bg = self._comp_bg_image(show_all=True)
        temp_fg = self._comp_fg_image(show_all=True)
        temp_active_layer_image = self._get_masked_image(self.model.layer.activeMask, show_all=True)
        composite = Image.alpha_composite(temp_bg, temp_active_layer_image)
        composite = Image.alpha_composite(composite, temp_fg)

        # send the PIL image to the uiModel to save to disk
        self.model.export_comp_image(composite)

    def _get_masked_image(self, layer_num, show_all=False):
        if layer_num < self.model.project.numMasks:
            mask = Image.fromarray(self.model.project.cvMasks[layer_num])
            mask.convert('L').resize(self.model.project.imgSize)
            image = Image.new('RGBA', self.model.project.imgSize, self.model.project.layerColors[layer_num + 1])
            if self.model.layer.visibility[layer_num] or show_all:
                image.putalpha(mask)
            else:
                image.putalpha(0)
            return image
        else:
            image = Image.new('RGBA', self.model.project.imgSize, 'magenta')
            image.putalpha(0)
            return image

    def _comp_bg_image(self, show_all=False):
        composite = Image.new('RGBA', self.model.project.imgSize, self.model.project.layerColors[0])
        for i in range(self.model.layer.activeMask):
            front = self._get_masked_image(i, show_all)
            composite = Image.alpha_composite(composite, front)
        return composite

    def _comp_fg_image(self, show_all=False):
        composite = self._get_masked_image(self.model.layer.activeMask + 1)
        for i in range(self.model.layer.activeMask + 1, self.model.project.numMasks):
            front = self._get_masked_image(i, show_all)
            composite = Image.alpha_composite(composite, front)
        return composite

    def _build_canvas_image(self):
        active_layer_image = self._get_masked_image(self.model.layer.activeMask)
        composite = Image.alpha_composite(self._bg_image, active_layer_image)
        composite = Image.alpha_composite(composite, self._fg_image)

        self.canvas.delete(ALL)

        # convert the PIL image to TK PhotoImage
        # set the canvas.image property, it wont work without this step
        self.canvas.image = ImageTk.PhotoImage(composite)
        self.canvas.create_image(0, 0, image=self.canvas.image, anchor=NW)

    def _render_brush_outline(self, x, y):
        r = self.model.brushSize
        self.canvas.create_oval(x - r, y - r, x + r, y + r)

    def _paint(self, e):
        if self.model.layer.visibility[self.model.layer.activeMask]:
            self._edit_active_mask(e, (255, 255, 255))
        else:
            self._prompt_show_invisible_active_layer()

    def _erase(self, e):
        if self.model.layer.visibility[self.model.layer.activeMask]:
            self._edit_active_mask(e, (0, 0, 0))
        else:
            self._prompt_show_invisible_active_layer()

    def _edit_active_mask(self, e, color):
        active_mask = self.model.project.cvMasks[self.model.layer.activeMask]
        if self._brush_position:
            cv.line(active_mask, self._brush_position, (e.x, e.y), color, self.model.brushSize * 2)
        else:
            self.model.save_undo()

        cv.circle(active_mask, (e.x, e.y), self.model.brushSize, color, -1)
        self._build_canvas_image()
        self._render_brush_outline(e.x, e.y)
        self._brush_position = (e.x, e.y)

    def _end_brush_stroke(self, _):
        self._brush_position = None
        if self.model.isCurrentSaved:
            self.model.set_mask_edited()

    def _mouse_move(self, e):
        self._build_canvas_image()
        self._render_brush_outline(e.x, e.y)

    def _mouse_exit(self, _):
        self._build_canvas_image()

    def _prompt_show_invisible_active_layer(self):
        layer_name = self.model.project.layerNames[self.model.layer.activeMask]
        message = "The active layer {} is hidden. Do you wish to make it visible to allow painting?".format(layer_name)
        is_ok = messagebox.askyesno(title="Confirm", message=message, icon="warning")

        if is_ok:
            self.model.toggle_layer_visibility(self.model.layer.activeMask)
