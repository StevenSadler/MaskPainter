from tkinter import *
from PIL import ImageTk, Image
import cv2 as cv
import numpy as np


class CanvasPainter:
    def __init__(self, canvas, model):
        self.canvas = canvas
        self.model = model
        self.model.subject.project.attach(self._update_project)
        self.model.subject.layer.attach(self._update_layer)

        # constants
        self._color_paint = 'white'
        self._color_erase = 'black'

        # vars needing reset
        self._bg_image = None
        self._fg_image = None
        self._brush_position = None
        self._pan_position = None

    def _update_layer(self):
        self._bg_image = self._comp_bg_image()
        self._fg_image = self._comp_fg_image()
        self.render_canvas_image()

    def _update_project(self):
        if self.model.isProjectLoaded:
            self._update_layer()

    def _refresh_zoom(self):
        # world space, canvas space, mask space need refresh after zoom
        pass

    def _get_mask(self, mask_num):
        cv_mask = self.model.project.cvMasks[mask_num]

        # get the minimum crop needed to fill the canvas
        crop = cv_mask[
               self.model.canvas.ms_crop_y:self.model.canvas.ms_crop_y + self.model.canvas.ms_crop_h,
               self.model.canvas.ms_crop_x:self.model.canvas.ms_crop_x + self.model.canvas.ms_crop_w
        ]

        zoom = self.model.canvas.zoom
        if zoom > 1:
            crop = np.kron(crop, np.ones((zoom, zoom), dtype=np.uint8))
        return crop

    def _get_masked_image(self, mask_num, show_all=False):
        ws_crop_size = self.model.canvas.ws_crop_size()
        if mask_num < self.model.project.numMasks:
            mask = Image.fromarray(self._get_mask(mask_num))
            mask.convert('L').resize(ws_crop_size)
            image = Image.new('RGBA', ws_crop_size, self.model.project.layerColors[mask_num + 1])
            if self.model.layer.visibility[mask_num] or show_all:
                image.putalpha(mask)
            else:
                image.putalpha(0)
            return image
        else:
            image = Image.new('RGBA', ws_crop_size, 'magenta')
            image.putalpha(0)
            return image

    def _comp_bg_image(self, show_all=False):
        composite = Image.new('RGBA', self.model.canvas.ws_crop_size(), self.model.project.layerColors[0])
        for i in range(self.model.layer.activeMask):
            front = self._get_masked_image(i, show_all)
            composite = Image.alpha_composite(composite, front)
        return composite

    def _comp_fg_image(self, show_all=False):
        composite = self._get_masked_image(self.model.layer.activeMask + 1, show_all)
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
        self.canvas.create_image(self.model.canvas.cs_crop_x, self.model.canvas.cs_crop_y,
                                 image=self.canvas.image, anchor=NW)

    def render_brush_outline(self, x, y):
        r = self.model.brushSize * self.model.canvas.zoom
        self.canvas.create_oval(x - r, y - r, x + r, y + r)

    ################################
    #
    #  controller calls
    #
    ################################

    def export_comp_image(self):
        temp_bg = self._comp_bg_image(show_all=True)
        temp_fg = self._comp_fg_image(show_all=True)
        temp_active_layer_image = self._get_masked_image(self.model.layer.activeMask, show_all=True)
        composite = Image.alpha_composite(temp_bg, temp_active_layer_image)
        composite = Image.alpha_composite(composite, temp_fg)

        # send the PIL image to the model to save to disk
        self.model.export_comp_image(composite)

    def resize(self):
        self._update_layer()

    def pan(self, e):
        if self._pan_position:
            old_x, old_y = self._pan_position
            dx = old_x - e.x
            dy = old_y - e.y
            self.model.canvas.move_camera_position(dx, dy)
            self._update_layer()
        self._pan_position = (e.x, e.y)

    def end_pan(self, _):
        self._pan_position = None

    def paint(self, e):
        self._edit_active_mask(e, (255, 255, 255))

    def erase(self, e):
        self._edit_active_mask(e, (0, 0, 0))

    def end_brush_stroke(self, _):
        self._brush_position = None
        if self.model.isCurrentSaved:
            self.model.set_mask_edited()

    def _edit_active_mask(self, e, color):
        active_mask = self.model.project.cvMasks[self.model.layer.activeMask]
        x, y = self.model.canvas.mouse_canvas_to_world(e)

        if self._brush_position:
            bx, by = self._brush_position
            cv.line(active_mask, (bx, by), (x, y), color, self.model.brushSize * 2)
        else:
            self.model.save_undo_state()

        cv.circle(active_mask, (x, y), self.model.brushSize, color, -1)
        self.render_canvas_image()
        self.render_brush_outline(e.x, e.y)
        self._brush_position = (x, y)
