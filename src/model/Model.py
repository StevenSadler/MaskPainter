from tkinter import filedialog, messagebox
import copy

from src.ObservableSubject import ObservableSubject
from src.model.ProjectModel import ProjectModel
from src.model.LayerModel import LayerModel
from src.model.CanvasModel import CanvasModel
from src.model.UndoHistory import UndoHistory


class Subject:
    def __init__(self):
        self.load = ObservableSubject()
        self.project = ObservableSubject()
        self.layer = ObservableSubject()
        self.zoom = ObservableSubject()
        self.undo = ObservableSubject()
        self.save = ObservableSubject()
        self.export = ObservableSubject()


class Model:
    def __init__(self, is_reset=False):
        if not is_reset:
            self.subject = Subject()
            self.project = ProjectModel()
            self.layer = LayerModel()
            self.canvas = CanvasModel()
            self._history = UndoHistory(20)

        # save subject
        self.isCurrentSaved = True

        # undo subject
        self._history.reset()

        # project subject
        self.isProjectLoaded = False
        self.project.unload()

        # integers
        self.brushSize = 10
        self.brushSizeMin = 2
        self.brushSizeMax = 40

    def _reset(self):
        self.__init__(True)

    def has_undo(self):
        return self.isProjectLoaded and self._history.has_undo()

    def has_redo(self):
        return self.isProjectLoaded and self._history.has_redo()

    # tk scale slider events are strings that contain floats
    # convert to int before storing
    def set_brush_size(self, event):
        self.brushSize = int(float(event))

    # change layer data and notify observers
    def set_active_layer(self, layer):
        self.layer.set_active_layer(layer)
        self.subject.layer.notify()

    def set_layer_visibility(self, layer, vis):
        self.layer.set_layer_visibility(layer, vis)
        self.subject.layer.notify()

    def toggle_layer_visibility(self, layer):
        self.layer.toggle_layer_visibility(layer)
        self.subject.layer.notify()

    def set_layer_name(self, layer, name):
        self.save_undo_state()
        self.project.layerNames[layer] = name
        self._notify_needs_save()

    def set_layer_color(self, layer, color):
        self.save_undo_state()
        self.project.layerColors[layer] = color
        self._notify_needs_save()

    def set_mask_edited(self):
        self.isCurrentSaved = False
        self.subject.save.notify()

    def export_comp_image(self, pil_image):
        self.project.export_comp_image(pil_image)
        self.subject.export.notify()

    def add_layer(self, layer):
        self.save_undo_state()
        self.project.insert_layer(layer)
        self.layer.insert_layer(layer - 1)
        self._notify_needs_save()

    def remove_layer(self, layer):
        # do not allow removing the last mask, what would happen to activeMask
        if self.project.numMasks > 1:
            self.save_undo_state()
            self.project.remove_layer(layer)
            self.layer.remove_layer(layer - 1)
            self._notify_needs_save()

    def zoom(self, zoom_factor):
        self.canvas.set_zoom(zoom_factor)
        self.subject.zoom.notify()

    def save_undo_state(self):
        project = copy.deepcopy(self.project)
        layer = copy.deepcopy(self.layer)
        self._history.save_state((project, layer))
        self.subject.undo.notify()

    def _notify_needs_save(self):
        self.isCurrentSaved = False
        self.subject.project.notify()
        self.subject.layer.notify()
        self.subject.save.notify()
        self.subject.undo.notify()

    ################################
    #
    #  menu click handlers
    #
    ################################

    def undo(self):
        if self._history.has_undo():
            self.project, self.layer = self._history.undo((self.project, self.layer))
            self._notify_needs_save()

    def redo(self):
        if self._history.has_redo():
            self.project, self.layer = self._history.redo((self.project, self.layer))
            self._notify_needs_save()

    def save(self):
        self.project.save()
        self.isCurrentSaved = True
        self.subject.save.notify()

    def prompt_save_as(self):
        project_file_path = filedialog.asksaveasfilename(title="Save as a new project json file",
                                                         defaultextension=".json",
                                                         filetypes=[("json files", "*.json")])
        if project_file_path:
            self.project.save_as(project_file_path)
            self._reset()

            self.load_project(project_file_path)

    def unload_project(self):
        if not self.isCurrentSaved:
            is_ok = messagebox.askyesno("Close Project", "You will lose any unsaved data. Are you sure?")
            if not is_ok:
                return

        self._reset()
        self.subject.load.notify()
        self.subject.project.notify()
        self.subject.save.notify()
        self.subject.undo.notify()

    def prompt_load_project(self):
        if not self.isCurrentSaved:
            is_ok = messagebox.askyesno("Open Project", "You will lose any unsaved data. Are you sure?")
            if not is_ok:
                return

        json_path = filedialog.askopenfilename()
        if json_path:
            self.load_project(json_path)

    def load_project(self, project_file_path):
        self.project.load_project(project_file_path)
        self.layer.init_model(self.project.numMasks)

        self.isProjectLoaded = True
        self.isCurrentSaved = True
        self.subject.load.notify()
        self.subject.project.notify()
        # self.subject.undo.notify()

    def prompt_create_project(self):
        if not self.isCurrentSaved:
            is_ok = messagebox.askyesno("Open Project", "You will lose any unsaved data. Are you sure?")
            if not is_ok:
                return

        project_file_path = filedialog.asksaveasfilename(title="Create a project json file",
                                                         defaultextension=".json",
                                                         filetypes=[("json files", "*.json")])
        if project_file_path:
            self.project.create_project(project_file_path)
            self.load_project(project_file_path)
