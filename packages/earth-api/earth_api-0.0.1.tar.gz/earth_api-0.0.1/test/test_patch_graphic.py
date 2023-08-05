from __future__ import absolute_import

import requests
import ssl
import json
import time
import os
import json
import csv
import sys
import argparse

expr_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../'))

if  expr_path not in sys.path:
    sys.path.insert(0, expr_path)

import unittest
import swagger_client
from swagger_client.api.graphics_api import GraphicsApi  # noqa: E501
from swagger_client.rest import ApiException
from test.utils import API_VERSION_CURRENT

from swagger_client.configuration import Configuration

ssl._create_default_https_context = ssl._create_unverified_context

# 0 - Successfully
# 1 - Failed

#region config
base_address = Configuration().host + "/arcgisearth" 
graphics_endpoint = "graphics"

def convert_to_absolute_path(rel_path):
    current_path = os.path.dirname(__file__)
    return os.path.join(current_path, rel_path)

patch_graphic_pos_path = "../Data/AutomationAPI/Graphic/patch_graphic_pos.json"
patch_graphic_pos_path = convert_to_absolute_path(patch_graphic_pos_path)
patch_graphic_pos_testcases_path = "../Data/AutomationAPI/Graphic/patch_graphic_pos_testcases.json"
patch_graphic_pos_testcases_path = convert_to_absolute_path(patch_graphic_pos_testcases_path)

patch_graphic_neg_path = "../Data/AutomationAPI/Graphic/patch_graphic_neg.json"
patch_graphic_neg_path = convert_to_absolute_path(patch_graphic_neg_path)
patch_graphic_neg_testcases_path = "../Data/AutomationAPI/Graphic/patch_graphic_neg_testcases.json"
patch_graphic_neg_testcases_path = convert_to_absolute_path(patch_graphic_neg_testcases_path)

patch_graphic_not_passed_path = convert_to_absolute_path("../Data/AutomationAPI/report/patch_graphic_not_passed.json")

#endregion

rlt_sucess   = '0'
rlt_error_1  = '1'

STATUS_CODE_200 = 200
STATUS_CODE_201 = 201
STATUS_CODE_204 = 204
STATUS_CODE_500 = 500

def save_testcases_json(testcases, json_path):
    safe_delete_file(json_path)

    with open(json_path, 'w') as jf:
        jf.write(json.dumps(testcases, indent=4))


def safe_delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)

def load_test_cases(json_path_array):
    cases = []
    for json_path in json_path_array:
        if not os.path.exists(json_path):
            continue

        with open(json_path, 'r') as f:
            case = json.load(f)
            cases.extend(case)
    return cases



# need follow the order
class EarthAutomationAPIPatchGraphicTest:

    def __init__(self, testcases_path):
        self._testcases_path = testcases_path
        if self._testcases_path is not None:
            self._test_cases = load_test_cases(self._testcases_path)
        
        self.sucess_added_graphics = []
        self.not_passed_cases = []

        self.api = GraphicsApi()  # noqa: E501
        self.version = API_VERSION_CURRENT

    def post_graphics(self, graphic):
    
        response_data = self.api.arcgisearth_graphics_post(
            _preload_content=False,
            async_req=False,
            body=graphic,
            api_version=self.version)
    
        content = response_data.data.decode('utf-8')
        results = json.loads(content)
        graphic_id = results["id"]

        return response_data.status, graphic_id
    
    def get_graphics(self, graphic_id):
        response_data = self.api.arcgisearth_graphics_id_get(
            id=graphic_id,
            _preload_content=False,
            async_req=False,
            api_version=self.version)

        content = response_data.data.decode('utf-8')
        results = json.loads(content)
        return results

    def patch_graphics(self, graphic):
    
        response_data = self.api.arcgisearth_graphics_patch(
            _preload_content=False,
            async_req=False,
            body=graphic,
            api_version=self.version)
    
        return response_data.status

    
    def delete_graphic(self, graphic_id):
        response_data = self.api.arcgisearth_graphics_id_delete(
            id=graphic_id,
            _preload_content=False,
            async_req=False,
            api_version=self.version)


    def test_patch_graphic_cases(self):
        url = base_address + graphics_endpoint 
        layer_array = []
        for case in self._test_cases:
            time.sleep(1)
            cid = case['cid']
            post_graphic = case['post_graphic']
            patch_graphic = case['patch_graphic']

            crlt = case['rlt']

            try:
                if "id" in post_graphic:
                    self.delete_graphic(post_graphic["id"])
            except Exception:
                pass

            status_code, graphic_id = self.post_graphics(post_graphic)
            if status_code == STATUS_CODE_201:
                self.sucess_added_graphics.append(post_graphic)
                if "id" not in post_graphic:
                    post_graphic["id"] = graphic_id
            else:
                print("No.{} Failed!".format(cid))
                self.not_passed_cases.append(case)
                continue

            time.sleep(1)

            try:
                status_code = self.patch_graphics(patch_graphic)

                if status_code == STATUS_CODE_204 and crlt == "0":

                        if 'response_graphic' in case:
                            expect_graphic = case['response_graphic']
                            time.sleep(1)
                            response_graphic = self.get_graphics(post_graphic["id"])

                            all_equal = True
                            if expect_graphic["id"] !=  response_graphic["id"]:
                                    all_equal = False
                        
                            if expect_graphic["geometry"] !=  response_graphic["geometry"]:
                                    all_equal = False

                            if expect_graphic["symbol"] !=  response_graphic["symbol"]:
                                    all_equal = False
                            if all_equal is not True:
                                print("No.{} Failed!".format(cid))
                                self.not_passed_cases.append(case)
                                continue
                        print("No.{} Passed!".format(cid))

                elif status_code != STATUS_CODE_204 and crlt == "1":
                    print("No.{} Passed!".format(cid))
                else:
                    print("No.{} Failed!".format(cid))
                    self.not_passed_cases.append(case)
                    continue
            except Exception as e:
                print("\n--------------------------------")

                if crlt == "1":
                    print("No.{} Passed!".format(cid))
                else:
                    print("No.{} Failed!".format(cid))
                    self.not_passed_cases.append(case)
                print(e)
                print("--------------------------------\n")
            #time.sleep(2)

            self.clear_added_graphic()

        save_testcases_json(self.not_passed_cases, patch_graphic_not_passed_path)
        if len(self.not_passed_cases) > 0:
            print("Some tests failed! More details: {}".format(patch_graphic_not_passed_path))
        else:
            print("All Passed!")

    
    def clear_added_graphic(self):
        for graphic in self.sucess_added_graphics: 
            if "id" in graphic:
                try:
                    self.delete_graphic(graphic_id=graphic["id"])
                except Exception:
                    pass
        self.sucess_added_graphics = []


def generate_test_cases():
    generate_pos_testcases()
    generate_neg_testcases()


def generate_pos_testcases():
    if not os.path.exists(patch_graphic_pos_path):
        raise "patch_graphic_neg_path not found"

    with open(patch_graphic_pos_path, 'r') as f:
        cases = json.load(f)

    test = EarthAutomationAPIPatchGraphicTest(None)
    for case in cases:
        cid = case['cid']
        post_graphic = case['post_graphic']
        patch_graphic = case['patch_graphic']
        status_code, graphic_id = test.post_graphics(post_graphic)
        time.sleep(2)
        status_code = test.patch_graphics(patch_graphic)
        time.sleep(2)
        respones_graphic = test.get_graphics(post_graphic["id"])
        case["response_graphic"] = respones_graphic
        test.delete_graphic(graphic_id)


    if os.path.exists(patch_graphic_pos_testcases_path):
        os.remove(patch_graphic_pos_testcases_path)

    with open(patch_graphic_pos_testcases_path, 'w') as jf:
        jf.write(json.dumps(cases, indent=4))

def generate_neg_testcases():
    if not os.path.exists(patch_graphic_neg_path):
        raise "add_graphic_neg_path not found"

    with open(patch_graphic_neg_path, 'r') as f:
        cases = json.load(f)

    if os.path.exists(patch_graphic_neg_testcases_path):
        os.remove(patch_graphic_neg_testcases_path)

    with open(patch_graphic_neg_testcases_path, 'w') as jf:
        jf.write(json.dumps(cases, indent=4))



def run_automatic_test():

    test = EarthAutomationAPIPatchGraphicTest([patch_graphic_pos_testcases_path, patch_graphic_neg_testcases_path])
    #test = EarthAutomationAPIPatchGraphicTest([patch_graphic_neg_testcases_path])
    #, patch_graphic_neg_testcases_path])
    test.test_patch_graphic_cases()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="test add graphic parser")
    parser.add_argument('-m', '--mode', help='test mode', default="test")
    args = parser.parse_args()
    mode = args.mode
    # generate testcases 
    # python test\test_patch_graphic.py -m gen
    # run test
    # python test\test_patch_graphic.py

    generate_test_cases()

    if mode == "test":
        run_automatic_test()
    elif mode == "gen":
        generate_test_cases()