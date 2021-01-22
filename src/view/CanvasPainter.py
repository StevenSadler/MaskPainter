from tkinter import *
from tkinter import messagebox
from PIL import ImageTk, Image
import cv2 as cv

from src.Utils import Utils


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
        self._pan_position = None
        self._color_paint = 'white'
        self._color_erase = 'black'

        self._img_x = 0
        self._img_y = 0

    def _update_layer(self):
        self._bg_image = self._comp_bg_image()
        self._fg_image = self._comp_fg_image()
        self.render_canvas_image()

    def _update_project(self):
        self.canvas.delete(ALL)
        if self.model.isProjectLoaded:
            self._update_layer()
            self.resize()
        else:
            self._img_x = 0
            self._img_y = 0

    def _update_export(self):
        temp_bg = self._comp_bg_image(show_all=True)
        temp_fg = self._comp_fg_image(show_all=True)
        temp_active_layer_image = self._get_masked_image(self.model.layer.activeMask, show_all=True)
        composite = Image.alpha_composite(temp_bg, temp_active_layer_image)
        composite = Image.alpha_composite(composite, temp_fg)

        # send the PIL image to the model to save to disk
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

    def render_canvas_image(self):
        active_layer_image = self._get_masked_image(self.model.layer.activeMask)
        composite = Image.alpha_composite(self._bg_image, active_layer_image)
        composite = Image.alpha_composite(composite, self._fg_image)

        self.canvas.delete(ALL)

        # convert the PIL image to TK PhotoImage
        # set the canvas.image property, it wont work without this step
        self.canvas.image = ImageTk.PhotoImage(composite)
        self.canvas.create_image(self._img_x, self._img_y, image=self.canvas.image, anchor=NW)

    def render_brush_outline(self, x, y):
        r = self.model.brushSize
        self.canvas.create_oval(x - r, y - r, x + r, y + r)

    ################################
    #
    #  controller calls
    #
    ################################

    def resize(self, _=None):
        img_w, img_h = self.model.project.imgSize
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()

        if canvas_w > img_w:
            self._img_x = (canvas_w - img_w) // 2
        else:
            self._img_x = Utils.clamp(self._img_x, 0, canvas_w - img_w)
        if canvas_h > img_h:
            self._img_y = (canvas_h - img_h) // 2
        else:
            self._img_y = Utils.clamp(self._img_y, 0, canvas_h - img_h)

        self.render_canvas_image()

    def pan(self, e):
        if self._pan_position:
            old_x, old_y = self._pan_position
            dx = e.x - old_x
            dy = e.y - old_y

            img_w, img_h = self.model.project.imgSize
            canvas_w = self.canvas.winfo_width()
            canvas_h = self.canvas.winfo_height()

            if canvas_w < img_w:
                self._img_x += dx
                self._img_x = Utils.clamp(self._img_x, 0, canvas_w - img_w)
            if canvas_h < img_h:
                self._img_y += dy
                self._img_y = Utils.clamp(self._img_y, 0, canvas_h - img_h)

        self._pan_position = (e.x, e.y)
        self.render_canvas_image()

    def end_pan(self, _):
        self._pan_position = None

    def paint(self, e):
        if self.model.layer.visibility[self.model.layer.activeMask]:
            self._edit_active_mask(e, (255, 255, 255))
        else:
            self._prompt_show_invisible_active_layer()

    def erase(self, e):
        if self.model.layer.visibility[self.model.layer.activeMask]:
            self._edit_active_mask(e, (0, 0, 0))
        else:
            self._prompt_show_invisible_active_layer()

    def end_brush_stroke(self, _):
        self._brush_position = None
        if self.model.isCurrentSaved:
            self.model.set_mask_edited()

    def _edit_active_mask(self, e, color):
        active_mask = self.model.project.cvMasks[self.model.layer.activeMask]
        x = e.x - self._img_x
        y = e.y - self._img_y
        if self._brush_position:
            bx, by = self._brush_position
            bx -= self._img_x
            by -= self._img_y
            cv.line(active_mask, (bx, by), (x, y), color, self.model.brushSize * 2)
        else:
            self.model.save_undo_state()

        cv.circle(active_mask, (x, y), self.model.brushSize, color, -1)
        self.render_canvas_image()
        self.render_brush_outline(e.x, e.y)
        self._brush_position = (e.x, e.y)

    def _prompt_show_invisible_active_layer(self):
        layer_name = self.model.project.layerNames[self.model.layer.activeMask]
        message = "The active layer {} is hidden. Do you wish to make it visible to allow painting?".format(
            layer_name)
        is_ok = messagebox.askyesno(title="Confirm", message=message, icon="warning")

        if is_ok:
            self.model.toggle_layer_visibility(self.model.layer.activeMask)