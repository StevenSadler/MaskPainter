import math

from src.Utils import Utils


class CanvasModel:
    def __init__(self, is_reset=False):
        if not is_reset:
            # constants
            self.min_zoom = 1
            self.max_zoom = 8

        # zoom vars
        self.zoom = 1

        # mask img vars
        self.mask_w = 0
        self.mask_h = 0

        # derived from zoom and mask img size
        self.world_w = 0
        self.world_h = 0

        #############################################

        # canvas vars
        self.canvas_w = 0
        self.canvas_h = 0

        # derived from zoom, mask img size, canvas size

        # world space vars
        self.ws_camera_x = 0
        self.ws_camera_y = 0
        self.ws_canvas_x = 0
        self.ws_canvas_y = 0
        self.ws_crop_x = 0
        self.ws_crop_y = 0
        self.ws_crop_w = 0
        self.ws_crop_h = 0

        # mask space vars
        self.ms_crop_x = 0
        self.ms_crop_y = 0
        self.ms_crop_w = 0
        self.ms_crop_h = 0

        # canvas space vars
        self.cs_crop_x = 0
        self.cs_crop_y = 0

        #############################################

    def reset(self):
        self.__init__(True)

    def ws_crop_size(self):
        return self.ws_crop_w, self.ws_crop_h

    def load(self, img_size, canvas_size):
        self.reset()

        self.canvas_w, self.canvas_h = canvas_size
        self.mask_w, self.mask_h = img_size
        self.world_w = self.mask_w * self.zoom
        self.world_h = self.mask_h * self.zoom
        self.ws_camera_x = self.world_w // 2
        self.ws_camera_y = self.world_h // 2

        self._derive_space_vars()

    def set_camera_position(self, world_space_x, world_space_y):
        old_x = self.ws_camera_x
        old_y = self.ws_camera_y
        self.ws_camera_x = world_space_x
        self.ws_camera_y = world_space_y
        self._clamp_camera()
        if self.ws_camera_x != old_x or self.ws_camera_y != old_y:
            self._derive_space_vars()

    def move_camera_position(self, dx, dy):
        self.set_camera_position(self.ws_camera_x + dx, self.ws_camera_y + dy)

    def resize_canvas(self, canvas_size):
        self.canvas_w, self.canvas_h = canvas_size

        # change the crop still centered on the old camera
        self._derive_ws_crop()

        # move the camera if it is too close to the edge of the world
        self._clamp_camera()

        # final change after clamped camera
        self._derive_space_vars()

    def mouse_canvas_to_world(self, e):
        # need no offset if canvas is larger than world
        # need positive offset if canvas is smaller than world
        x_offset = max(0, self.ws_canvas_x)
        y_offset = max(0, self.ws_canvas_y)
        x = (e.x - self.cs_crop_x) // self.zoom + x_offset
        y = (e.y - self.cs_crop_y) // self.zoom + y_offset
        return x, y

    ###########################################################################
    #
    #  helpers
    #
    ###########################################################################

    def _clamp_camera(self):
        left = self.ws_crop_w // 2
        right = self.world_w - int(math.ceil(self.ws_crop_w / 2.0))
        self.ws_camera_x = Utils.clamp(self.ws_camera_x, left, right)

        top = self.ws_crop_h // 2
        bottom = self.world_h - int(math.ceil(self.ws_crop_h / 2.0))
        self.ws_camera_y = Utils.clamp(self.ws_camera_y, top, bottom)

    def _derive_ws_crop(self):
        # world space vars
        self.ws_crop_w = min(self.world_w, self.canvas_w)
        self.ws_crop_h = min(self.world_h, self.canvas_h)
        self.ws_crop_x = self.ws_camera_x - self.ws_crop_w // 2
        self.ws_crop_y = self.ws_camera_y - self.ws_crop_h // 2

    def _derive_space_vars(self):
        # world space vars
        self._derive_ws_crop()
        self.ws_canvas_x = self.ws_camera_x - self.canvas_w // 2
        self.ws_canvas_y = self.ws_camera_y - self.canvas_h // 2

        # mask space vars
        self.ms_crop_x = self.ws_crop_x // self.zoom
        self.ms_crop_y = self.ws_crop_y // self.zoom
        self.ms_crop_w = int(math.ceil(self.ws_crop_w / self.zoom))
        self.ms_crop_h = int(math.ceil(self.ws_crop_h / self.zoom))
        # self.ms_crop_size = (self.ms_crop_w, self.ms_crop_h)

        # canvas space vars
        self.cs_crop_x = self.ws_crop_x - self.ws_canvas_x
        self.cs_crop_y = self.ws_crop_y - self.ws_canvas_y
