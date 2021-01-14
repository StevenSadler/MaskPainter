class StatusPanel:
    def __init__(self, status, model):
        self.status = status
        self.model = model
        self.model.subject.layer.attach(self._update_layer)
        self.model.subject.project.attach(self._update_project)
        self.model.subject.save.attach(self._update_save)
        self.model.subject.export.attach(self._update_export)

    def _update_layer(self):
        active_layer = self.model.activeLayer
        vis = self.model.layerVisibility
        self.status.config(text="Update: LAYER: active={} vis={}".format(active_layer, vis))

    def _update_project(self):
        if self.model.isProjectLoaded:
            self.status.config(text="Update: PROJECT: {}".format(self.model.project.projectPath))
        else:
            self.status.config(text="Update: PROJECT: unloaded")

    def _update_save(self):
        if self.model.isProjectLoaded and self.model.isCurrentSaved:
            self.status.config(text="Update: SAVE: project={} masks={}".format(self.model.project.projectName,
                                                                               self.model.project.maskFileNames))

    def _update_export(self):
        self.status.config(text="Update: EXPORT: {}".format(self.model.project.compFileName))
