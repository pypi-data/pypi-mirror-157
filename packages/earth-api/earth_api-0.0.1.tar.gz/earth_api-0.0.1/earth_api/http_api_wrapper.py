# -*- coding:utf-8 -*-
import os
import sys
import requests
import json

automation_api_root_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../'))

if  automation_api_root_path not in sys.path:
    sys.path.insert(0, automation_api_root_path)

from swagger_client.configuration import Configuration

base_address = Configuration().host + "/arcgisearth" 
api_version_1 = "?api-version=1.0"
api_version_latest = "?api-version=latest"
layer_endpoint = "/layer"
layers_endpoint = "/layers"

graphics_url = "http://localhost:8000/arcgisearth/graphics"


from earth_api.api_wrapper import BasicAPIWrapper

class HttpAPIWrapper(BasicAPIWrapper):

    def __init__(self, api_version="1.16"):
        super().__init__(api_version)
    
    
    def get_camera(self):
        pass

    def set_camera(self, camera):
        url = base_address + "/camera" 
        r = requests.put(url, data=json.dumps(camera), verify=False)
        return r.status_code, r.json()

    def set_flight(self, flight):
        url = base_address + "/flyto"
        r = requests.put(url, data=json.dumps(flight), verify=False)
        return r.status_code, r.json()

    def add_layer(self, layer):
        url = base_address + layer_endpoint +  api_version_latest
        headers = {"content-Type": "application/json"}

        r = requests.post(url, data=json.dumps(layer),
                            headers=headers, verify=False)
        return r.status_code, r.data.decode('utf-8')

    def get_layer(self, layer_id):
        url = base_address + layer_endpoint + "/" + layer_id + api_version_latest
        r = requests.get(url, verify=False)
        return r.status_code, r.json()

    def remove_layer(self, layer_id):
        url = base_address + "/layer/" + layer_id
        r = requests.delete(url)
        return r.status_code, r.json()

    def clear_layers(self, layers_info):
        url = base_address + layers_endpoint + "/AllLayers" + api_version_latest
        r = requests.delete(url, verify=False)

    def add_graphic(self, graphic):
        headers={'content-Type': 'application/json'}
        graphic_json_str = json.dumps(graphic)
        response = requests.post(graphics_url, data=graphic_json_str, headers=headers,verify=False)
        return response.status_code, response.content.decode("utf-8")

    def get_graphic(self, graphic_id):
        raise "Not implemented"
        pass

    def update_graphic(self, graphic):
        raise "Not implemented"
        pass

    def remove_graphic(self, graphic_id):
        raise "Not implemented"
        pass

    def clear_graphics(self):
        requests.delete(graphics_url)

    def add_drawing(self, drawing):
        raise "Not implemented"
        pass

    def remove_drawing(self, drawing_id):
        raise "Not implemented"
        pass

    def clear_drawings(self):
        raise "Not implemented"
        pass

    def get_workspace(self):
        raise "Not implemented"
        pass

    def import_workspace(self, workspace_info):
        url = base_address + "/workspace"
        data = json.dumps(workspace_info)
        r = requests.put(url, data=data, stream=True)

    def clear_workspace(self):
        raise "Not implemented"

    def get_snapshot(self):
        raise "Not implemented"
        pass