class LayerModel:
    def __init__(self):
        self.activeMask = 0        # change this to active
        self.visibility = []   # change this to visibility

    def init_model(self, num_masks):
        self.activeMask = 0
        self.visibility = []
        for i in range(num_masks):
            self.visibility.append(True)

    def set_active_layer(self, layer):
        self.activeMask = layer
        self.visibility[layer] = True

    def set_layer_visibility(self, layer, vis):
        self.visibility[layer] = vis

    def toggle_layer_visibility(self, layer):
        self.visibility[layer] = not self.visibility[layer]

    def insert_layer(self, layer):
        self.visibility.insert(layer, True)
        self.activeMask = layer
