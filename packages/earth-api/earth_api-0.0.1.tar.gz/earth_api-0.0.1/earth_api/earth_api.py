# -*- coding:utf-8 -*-
import os
import sys
automation_api_root_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../'))

if  automation_api_root_path not in sys.path:
    sys.path.insert(0, automation_api_root_path)


from earth_api.http_api_wrapper import HttpAPIWrapper
from earth_api.swagger_api_wrapper import SwaggerAPIWrapper

class EarthAPI:

    def __init__(self, type="swagger", version='latest') -> None:
        # not support version for now
        if type == "http":
            self.api_wrapper = HttpAPIWrapper()
        else:
            self.api_wrapper = SwaggerAPIWrapper()
    
    def get_camera(self):
        return self.api_wrapper.get_camera()

    def set_camera(self, camera):
        return self.api_wrapper.set_camera(camera)

    def set_flight(self, flight):
        return self.api_wrapper.set_flight(flight)

    def add_layer(self, layer):
        return self.api_wrapper.add_layer(layer)

    def get_layer(self, layer_id):
        return self.api_wrapper.get_layer(layer_id)

    def remove_layer(self, layer_id):
        return self.api_wrapper.remove_layer(layer_id)

    def clear_layers(self, layers_info):
        return self.api_wrapper.clear_layers(layers_info)

    def add_graphic(self, graphic):
        return self.api_wrapper.add_graphic(graphic)

    def get_graphic(self, graphic_id):
        return self.api_wrapper.get_graphic(graphic_id)

    def update_graphic(self, graphic):
        return self.api_wrapper.update_graphic(graphic)

    def remove_graphic(self, graphic_id):
        return self.api_wrapper.remove_graphic(graphic_id)

    def clear_graphics(self):
        return self.api_wrapper.clear_graphics()

    def add_drawing(self, drawing):
        return  self.api_wrapper.add_drawing(drawing)

    def remove_drawing(self, drawing_id):
        return self.api_wrapper.remove_drawing(drawing_id)

    def clear_drawings(self):
        return self.api_wrapper.clear_drawings()

    def get_workspace(self):
        return self.api_wrapper.get_workspace()

    def import_workspace(self, workspace_info):
        return self.api_wrapper.import_workspace(workspace_info)

    def clear_workspace(self):
        return self.api_wrapper.clear_workspace()

    def get_snapshot(self):
        return self.api_wrapper.get_snapshot()