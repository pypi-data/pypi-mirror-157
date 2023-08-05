class BasicAPIWrapper:
    # from http://localhost:8000/sample/index.html

    def __init__(self, api_version) -> None:
        self.version = api_version
        pass
    
    def get_camera(self):
        pass

    def set_camera(self, camera):
        pass

    def set_flight(self, flight):
        pass

    def add_layer(self, layer):
        pass

    def get_layer(self, layer_id):
        pass

    def remove_layer(self, layer_id):
        pass

    def clear_layers(self, layers_info):
        pass

    def add_graphic(self, graphic):
        pass

    def get_graphic(self, graphic_id):
        pass

    def update_graphic(self, graphic):
        pass

    def remove_graphic(self, graphic_id):
        pass

    def clear_graphics(self):
        pass

    def add_drawing(self, drawing):
        pass

    def remove_drawing(self, drawing_id):
        pass

    def clear_drawings(self):
        pass

    def get_workspace(self):
        pass

    def import_workspace(self, workspace_info):
        pass

    def clear_workspace(self):
        pass

    def get_snapshot(self):
        pass