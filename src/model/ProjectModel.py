import json
from types import SimpleNamespace
import os
import cv2 as cv
import numpy as np

from src.Utils import Utils


# class Layer:
#     def __init__(self, name, color, cv_mask, visible):
#         self.name = name
#         self.color = color
#         self.cvMask = cv_mask
#         self.visible = visible


class ProjectModel:
    def __init__(self):
        self._config_file_path = "MaskPainter_config.json"
        self._comp_dir = "comp"
        self._mask_dir = "mask"

        self.default_background_color = "#3399ff"

        self.projectPath = None          # ie. 'C:/some_path/app_root/projects/example_project.json'
        self.projectFileName = None      # ie. 'example_project.json'
        self.projectName = None          # ie. 'example_project'
        self.compRootDir = None          # ie. 'C:/some_path/app_root/projects/comp/'
        self.maskRootDir = None          # ie. 'C:/some_path/app_root/projects/mask/'

        self.backgroundImagePath = None
        self.cvBackgroundImage = None

        self.layerColors = []
        self.layerNames = []
        self.cvMasks = []

        self.visibility = []
        self.activeMask = 0
        self.maskOpaque = False

        self.imgSize = None
        self.numMasks = None

    def unload(self):
        self.__init__()

    @staticmethod
    def _generate_comp_file_name(image_prefix):
        return "{}_comp.png".format(image_prefix)

    @staticmethod
    def _generate_mask_file_name(image_prefix, image_num):
        return "{}_mask{}.jpg".format(image_prefix, image_num)

    @staticmethod
    def _write_default_config(config_file_path):
        dictionary = {
            "default_project_settings": {
                "mask_width": 640,
                "mask_height": 360,
                "layer_colors": ["#ffffb3", "#b3ff99", "#dfbf9f"],
                "layer_names": ["Lowlands", "Hills", "Mountains"],
                "layer_viz": [True, True, True],
                "active_mask": 0,
                "mask_opaque": True
            }
        }
        with open(config_file_path, 'w') as outfile:
            json.dump(dictionary, outfile, indent=4)
        outfile.close()

    @staticmethod
    def _read_json_file(file_path):
        f = open(file_path)
        obj = json.load(f, object_hook=lambda d: SimpleNamespace(**d))
        f.close()
        return obj

    def export_comp_image(self, pil_image):
        if not os.path.exists(self.compRootDir):
            os.mkdir(self.compRootDir)
        outfile = os.path.join(self.compRootDir, self._generate_comp_file_name(self.projectName))
        pil_image.save(outfile)

    def save_as(self, project_file_path):
        self._set_paths(project_file_path)
        self._save_project_json()
        self._save_masks()

        # model will use subject to update observer views

    def save(self):
        self._save_project_json()
        self._save_masks()

    def create_project(self, project_file_path, bg_image_file_path=None):
        self.unload()
        if bg_image_file_path:
            self.backgroundImagePath = bg_image_file_path
        self._set_paths(project_file_path)
        self._read_default_config(self._config_file_path, self.projectName)
        self._save_project_json()
        self._save_masks()

        # model will use subject to update observer views

    def load_project(self, project_file_path):
        self.unload()
        self._set_paths(project_file_path)
        self._read_project_json(project_file_path)

        # model will use subject to update observer views

    def _set_paths(self, project_file_path):
        self.projectPath = project_file_path
        project_root_dir, self.projectFileName = os.path.split(self.projectPath)
        self.projectName = self.projectFileName.split('.')[0]
        self.compRootDir = os.path.join(project_root_dir, self._comp_dir)
        self.maskRootDir = os.path.join(project_root_dir, self._mask_dir)

    def _read_default_config(self, config_file_path, image_prefix):
        if not os.path.exists(config_file_path):
            self._write_default_config(config_file_path)

        obj = self._read_json_file(config_file_path)
        config = obj.default_project_settings

        # derive data from config
        self.layerColors = config.layer_colors
        self.layerNames = config.layer_names
        self.visibility = config.layer_viz
        self.maskOpaque = config.mask_opaque

        # fill in the missing data
        self.numMasks = len(self.layerNames)
        self.cvMasks = []

        if self.backgroundImagePath:
            # need to get h and w from background image
            temp_bg = cv.imread(self.backgroundImagePath)
            print("temp bg shape {}".format(temp_bg.shape))
            h = temp_bg.shape[0]
            w = temp_bg.shape[1]
        else:
            h = config.mask_height
            w = config.mask_width

        for i in range(self.numMasks):
            self.cvMasks.append(np.zeros((h, w, 3), dtype=np.uint8))
        self.imgSize = (w, h)

    def _read_project_json(self, project_file_path):
        obj = self._read_json_file(project_file_path)

        if hasattr(obj, "background_image_path"):
            self.backgroundImagePath = obj.background_image_path
            cv_bg = cv.imread(self.backgroundImagePath)
            self.cvBackgroundImage = cv.cvtColor(cv_bg, cv.COLOR_BGR2RGBA)

        # derive data from project file
        self.layerColors = obj.layer_colors
        self.layerNames = obj.layer_names
        self.visibility = obj.layer_viz
        self.activeMask = obj.active_mask
        self.maskOpaque = obj.mask_opaque
        self.numMasks = len(obj.layer_names)
        self.cvMasks = []
        for i in range(self.numMasks):
            mask_filename = self._generate_mask_file_name(self.projectName, i + 1)
            mask_path = os.path.join(self.maskRootDir, mask_filename)
            cv_mask_bgr = cv.imread(mask_path)
            cv_mask = cv.cvtColor(cv_mask_bgr, cv.COLOR_BGR2GRAY)
            self.cvMasks.append(cv_mask)

        # fill in the missing data
        self.imgSize = (self.cvMasks[0].shape[1], self.cvMasks[0].shape[0])

    def _save_project_json(self):
        # build a json from python data
        # save json to file
        dictionary = {
            "project_name": self.projectName,
            "layer_colors": self.layerColors,
            "layer_names": self.layerNames,
            "layer_viz": self.visibility,
            "active_mask": self.activeMask,
            "mask_opaque": self.maskOpaque
        }
        if self.backgroundImagePath:
            dictionary["background_image_path"] = self.backgroundImagePath

        with open(self.projectPath, 'w') as outfile:
            json.dump(dictionary, outfile, indent=4)
        outfile.close()

    def _save_masks(self):
        if not os.path.exists(self.maskRootDir):
            os.mkdir(self.maskRootDir)
        for i in range(self.numMasks):
            mask_filename = self._generate_mask_file_name(self.projectName, i+1)
            cv.imwrite(os.path.join(self.maskRootDir, mask_filename), self.cvMasks[i])

    def insert_layer(self, layer):
        # insert in layer colors, layer names, cv masks
        if layer == 0:
            color = self.layerColors[layer]
        elif layer >= self.numMasks:
            color = self.layerColors[layer-1]
        else:
            color = Utils.average_hex_colors(self.layerColors[layer-1], self.layerColors[layer])

        self.layerColors.insert(layer, color)
        self.layerNames.insert(layer, "New layer")
        self.visibility.insert(layer, True)
        w, h = self.imgSize
        cv_mask_bgr = np.zeros((h, w, 3), dtype=np.uint8)
        cv_mask = cv.cvtColor(cv_mask_bgr, cv.COLOR_BGR2GRAY)
        self.cvMasks.insert(layer, cv_mask)
        self.numMasks = len(self.cvMasks)

    def remove_layer(self, layer):
        self.layerColors.pop(layer)
        self.layerNames.pop(layer)
        self.visibility.pop(layer)
        self.cvMasks.pop(layer)
        self.numMasks = len(self.cvMasks)

        if self.activeMask == layer:
            self.activeMask = 0

    # refactored here from LayerModel
    def set_active_layer(self, layer):
        self.activeMask = layer
        self.visibility[layer] = True

    def set_layer_visibility(self, layer, vis):
        self.visibility[layer] = vis

    def toggle_layer_visibility(self, layer):
        self.visibility[layer] = not self.visibility[layer]

    def toggle_mask_opacity(self):
        self.maskOpaque = not self.maskOpaque

