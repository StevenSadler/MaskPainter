from tkinter import filedialog, messagebox

from src.ObservableSubject import ObservableSubject
from src.model.ProjectModel import ProjectModel


class Subject:
    def __init__(self):
        self.layer = ObservableSubject()
        self.project = ObservableSubject()
        self.save = ObservableSubject()
        self.export = ObservableSubject()  # used as a one-time event for an export request


class Model:
    def __init__(self, is_reset=False):
        if not is_reset:
            self.subject = Subject()
            self.project = ProjectModel()

        # save subject
        self.isCurrentSaved = True

        # layer subject
        self.activeLayer = 0
        self.layerVisibility = []

        # project subject
        self.isProjectLoaded = False
        self.project.unload()

        # integers
        self.brushSize = 10
        self.brushSizeMin = 2
        self.brushSizeMax = 40

    def _reset(self):
        self.__init__(True)

    # tk scale slider events are strings that contain floats
    # convert to int before storing
    def set_brush_size(self, event):
        self.brushSize = int(float(event))

    # change layer data and notify observers
    def set_active_layer(self, layer):
        self.activeLayer = layer
        self.layerVisibility[layer] = True
        self.subject.layer.notify()

    def set_layer_visibility(self, layer, vis):
        self.layerVisibility[layer] = vis
        self.subject.layer.notify()

    def toggle_layer_visibility(self, layer):
        self.layerVisibility[layer] = not self.layerVisibility[layer]
        self.subject.layer.notify()

    def set_layer_name(self, layer, name):
        self.project.layerNames[layer] = name
        self.isCurrentSaved = False
        self.subject.project.notify()
        self.subject.save.notify()

    def set_layer_color(self, layer, color):
        self.project.layerColors[layer] = color
        self.isCurrentSaved = False
        self.subject.project.notify()
        self.subject.save.notify()

    def set_mask_edited(self):
        self.isCurrentSaved = False
        self.subject.save.notify()

    def export_comp_image(self, pil_image):
        self.project.export_comp_image(pil_image)

    ################################
    #
    #  menu click handlers
    #
    ################################

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
            self.isProjectLoaded = True
            self.isCurrentSaved = True
            self.subject.project.notify()

    def unload_project(self):
        if not self.isCurrentSaved:
            is_ok = messagebox.askyesno("Close Project", "You will lose any unsaved data. Are you sure?")
            if not is_ok:
                return

        self._reset()
        self.subject.project.notify()
        self.subject.save.notify()

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

        self.layerVisibility = []
        for i in range(self.project.numMasks):
            self.layerVisibility.append(True)

        self.isProjectLoaded = True
        self.isCurrentSaved = True
        self.subject.project.notify()

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
