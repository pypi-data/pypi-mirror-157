from __future__ import absolute_import

import requests
import ssl
import unittest
import json
import time
import os
import json
import operator
import csv

import os
import sys
expr_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../'))

if  expr_path not in sys.path:
    sys.path.insert(0, expr_path)


import unittest
import json
import time

import swagger_client
from swagger_client.api.layer_api import LayerApi  # noqa: E501
from swagger_client.rest import ApiException
from swagger_client.configuration import Configuration


ssl._create_default_https_context = ssl._create_unverified_context

# 0 - Successfully. 表示成功
# 1 - Failed: json parsing error. 表示失败，json parsing error
# 2 - Failed, not signed in. 表示没有sign的失败类型
# 3 - Failed, Error from Earth application level. 表示来自app层的error
# 4 - Failed, syntax error. 表示失败，syntax error
# 5 - Failed, Unsupported data type. 表示失败，unsupported data type, earth core level
# 6 - Data loaded Successfully, but there is an error
# 7 - Successfully. API定义为成功，子图层加载失败，当前数据加载成功。多见于mspk等数据中。
# 8 - Failed, Unsupported data type. 表示失败，unsupported data type, automation api level

#region config
base_address = Configuration().host + "/arcgisearth" 
api_version_1 = "?api-version=1.0"
layer_endpoint = "/layer"
layers_endpoint = "/layers"

add_layer_status_code_field = "addLyrStatusCode"
get_layer_status_code_field = "getLyrStatusCode"


def convert_to_absolute_path(rel_path):
    current_path = os.path.dirname(__file__)
    return os.path.join(current_path, rel_path)

neg_add_layer_result_json_path = convert_to_absolute_path("../Data/AutomationAPI/report/negative_add_layer_result.json")
pos_add_layer_result_json_path = convert_to_absolute_path("../Data/AutomationAPI/report/positive_add_layer_result.json")

pos_testcases_json_path = convert_to_absolute_path("../Data/AutomationAPI/report/positive_testcases.json")
neg_testcases_json_path = convert_to_absolute_path("../Data/AutomationAPI/report/negative_testcases.json")

neg_get_added_layer_result_json_path = convert_to_absolute_path("../Data/AutomationAPI/report/negative_get_added_layer_result.json")
pos_get_added_layer_result_json_path = convert_to_absolute_path("../Data/AutomationAPI/report/positive_get_added_layer_result.json")

negative_addlayer_notpass_json_path = convert_to_absolute_path("../Data/AutomationAPI/report/negative_not_pass.json")
positive_addlayer_notpass_json_path = convert_to_absolute_path("../Data/AutomationAPI/report/positive_not_pass.json")

disable_error_type_2 = True 
sleep_time_after_add_neg_layer = 50 # unit seconds
sleep_time_after_add_pos_layer = 50 # unit seconds, as we change the add layer logic
sleep_time_between_add_pos_layer = 2 # unit seconds
#endregion

rlt_sucess = '0'
rlt_error_1 = '1'
rlt_error_2 = '2'
rlt_error_3 = '3'
rlt_error_4 = '4'
rlt_error_5 = '5'
rlt_error_6 = '6'
rlt_error_7 = '7'
rlt_error_8 = '8'

STATUS_CODE_200 = 200
STATUS_CODE_500 = 500


def safe_delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)

def generate_testcases(csv_paths):

    positive_testcases = []
    negative_testcases = []

    for csv_path in csv_paths:

        if csv_path is None or csv_path == '':
            return

        if 'http' in csv_path:
            csv_path = downloader(csv_path)

        if not os.path.exists(csv_path):
            return

        with open(csv_path) as cf:
            csv_reader = csv.reader(cf)
            csv_header = next(csv_reader)
            for row in csv_reader:
                cid = row[0]
                type = row[1]
                url = row[2]
                target = row[3]
                result = row[4]

                layer_info = generate_layer_info(type, url, target)
                testcase = {}
                testcase["cid"] = cid 
                testcase["lyr"] =  layer_info
                if result == '0':
                    positive_testcases.append(testcase)
                elif disable_error_type_2 == True and result == rlt_error_2:
                    continue
                else:
                    testcase['rlt'] = row[4]
                    negative_testcases.append(testcase)

    num_pos_cases = len(positive_testcases)
    num_neg_cases = len(negative_testcases)
    num_all_cases = (num_pos_cases + num_neg_cases)

    print("Total cases:{}\n Positive cases:{}\n Negative cases:{}\n".format(num_all_cases, num_pos_cases, num_neg_cases))
    return positive_testcases, negative_testcases

def save_testcases_json(layers, json_path):
    safe_delete_file(json_path)

    with open(json_path, 'w') as jf:
        jf.write(json.dumps(layers, indent=4))

def load_test_cases(json_path):
    if not os.path.exists(json_path):
        return []

    with open(json_path, 'r') as f:
        cases = json.load(f)
        return cases


def generate_layer_info(type, url, target):
    layer_info = {}

    if ';' in url: 
        urls = url.split(';')
        layer_info['URIs'] = urls
    else:
        layer_info['URI'] = url.strip()
    if target is not None or target != '':
        layer_info['target'] = target.strip()
    if type is not None or target != '':
        layer_info['type'] = type.strip()

    return layer_info


def delete_all_layers():
    url = base_address + layers_endpoint + "/AllLayers" + api_version_1
    r = requests.delete(url, verify=False)

def load_test_cases(json_path):
    if not os.path.exists(json_path):
        return []

    with open(json_path, 'r') as f:
        cases = json.load(f)
        return cases

def downloader(url):
    file_name = url.split('/')[-1].split('?')[0]
    file_name = "./result/" + file_name
    safe_delete_file(file_name)

    file_data = requests.get(url, allow_redirects=True).content
    with open(file_name, 'wb') as handler:
        handler.write(file_data)
    return file_name


# need follow the order
class EarthAutomationAPILayerTest:

    def __init__(self, csv_paths=None, pos_cases_path=None, neg_cases_path=None):
        if csv_paths is not None and len(csv_paths) > 0:
            self._pos_cases, self._neg_cases = generate_testcases(csv_paths)
            save_testcases_json(self._pos_cases, pos_testcases_json_path)
            save_testcases_json(self._neg_cases, neg_testcases_json_path)
        if pos_cases_path is not None and os.path.exists(pos_cases_path):
            self._pos_cases = load_test_cases(pos_cases_path)

        if neg_cases_path is not None and os.path.exists(neg_cases_path):
            self._neg_cases = load_test_cases(pos_cases_path)

    def get_lyr_json(self, lyr):
        return json.dumps(lyr)

    def test_add_layers_pos_cases_step1(self):
        not_passed_cases = []
        url = base_address + layer_endpoint + api_version_1 
        layer_array = []
        for case in self._pos_cases:
            time.sleep(1)
            cid = case['cid']
            lyr = case['lyr']
            layer_id = None
            layer_json_str = self.get_lyr_json(lyr)
            headers = {"content-Type": "application/json"}
            r = requests.post(url, data=layer_json_str,
                              headers=headers, verify=False)
            if r.status_code == STATUS_CODE_200 or r.status_code == STATUS_CODE_500:
                content = r.content.decode('utf-8')
                if content != '':
                    results = json.loads(content)
                    if r.status_code == STATUS_CODE_200:
                        if "id" in results:
                            layer_id = results["id"]
                        else:
                            print("No.{} Failed!".format(cid))
                            not_passed_cases.append(case)
                            continue
                    else:
                        layer_id = None
                    if r.status_code == STATUS_CODE_500:
                        content = r.content.decode('utf-8')
                        erro_info = json.loads(content)
                        case['errorMessage'] = erro_info['errorMessage']

                    case['lid'] = layer_id 
                    case[add_layer_status_code_field] = r.status_code
                    print("No.{} Status Code: {}".format(cid, r.status_code))
                    layer_array.append(case)
                time.sleep(sleep_time_between_add_pos_layer)
            else:
                print("No.{} Failed!".format(cid))
                not_passed_cases.append(case)
            

        save_testcases_json(not_passed_cases, positive_addlayer_notpass_json_path)
        save_testcases_json(layer_array, pos_add_layer_result_json_path)


    def test_add_layers_neg_cases_step1(self):
        not_passed_cases = []
        url = base_address + layer_endpoint + api_version_1 
        layer_array = []
        for case in self._neg_cases:
            cid = case['cid']
            lyr = case['lyr']
            layer_id = None
            layer_json_str = self.get_lyr_json(lyr)            
            headers = {"content-Type": "application/json"}
            r = requests.post(url, data=layer_json_str,
                              headers=headers, verify=False)
            if r.status_code == STATUS_CODE_200 or r.status_code == STATUS_CODE_500:
                content = r.content.decode('utf-8')
                if content != '':
                    results = json.loads(content)
                    if r.status_code == STATUS_CODE_200:
                        layer_id = results["id"]
                    else:
                        layer_id = None
                    if r.status_code == STATUS_CODE_500:
                        content = r.content.decode('utf-8')
                        erro_info = json.loads(content)
                        case['errorMessage'] = erro_info['errorMessage']

                    case['lid'] = layer_id 
                    case[add_layer_status_code_field] = r.status_code
                    print("No.{} Status Code: {}".format(cid, r.status_code))
                    layer_array.append(case)
            else:
                print("No.{} Failed!".format(cid))
                not_passed_cases.append(case)

        save_testcases_json(not_passed_cases, negative_addlayer_notpass_json_path)
        save_testcases_json(layer_array, neg_add_layer_result_json_path)


    def pos_get_added_layer(self):
        all_passed = True 
        layer_array = None
        with open(pos_add_layer_result_json_path, 'r') as jf:
            layer_array = json.loads(jf.read())
            result_array = []
        if len(layer_array) > 0:
            for layer in layer_array:
                lyr = layer.copy()
                status_code = lyr[add_layer_status_code_field]
                passTest = False
                if status_code == STATUS_CODE_200:
                    url = base_address + layer_endpoint + "/" + lyr['lid'] + api_version_1
                    r = requests.get(url, verify=False)

                    if r.status_code == STATUS_CODE_200:
                        content = r.content.decode('utf-8')
                        layer_info = json.loads(content)
                        layer_load_status_string = layer_info["loadStatus"]
                        lyr['loadStatus'] = layer_load_status_string
                        if layer_load_status_string == 'Loaded': 
                            passTest = True

                if all_passed is True and passTest is False:
                    all_passed = False

                lyr['passTestResult'] = passTest
                print("Cid:{} Passed:{}".format(lyr['cid'], passTest))
                result_array.append(lyr)
            save_testcases_json(result_array, pos_get_added_layer_result_json_path)
            return all_passed
 


    def neg_get_added_layer(self):
        layer_array = None
        with open(neg_add_layer_result_json_path, 'r') as jf:
            layer_array = json.loads(jf.read())
            result_array = []
        if len(layer_array) > 0:
            for layer in layer_array:
                lyr = layer.copy()
                status_code = lyr[add_layer_status_code_field]
                rlt = lyr['rlt']

                lyr['passTestResult'] = False 

                if status_code == STATUS_CODE_500:
                    errorMessageStr = lyr['errorMessage']
                    if rlt == rlt_error_4:
                        if errorMessageStr.find("Syntax error") >= 0:
                            lyr['passTestResult'] = True
                        else:
                            lyr['passTestResult'] = False
                    elif rlt == rlt_error_8 or rlt == rlt_error_5:
                        if errorMessageStr.find("Unsupported layer") >= 0:
                            lyr['passTestResult'] = True
                    elif rlt == rlt_error_3:
                        lyr['passTestResult'] = True

                elif status_code == STATUS_CODE_200:
                    url = base_address + layer_endpoint + "/" + lyr['lid'] + api_version_1
                    r = requests.get(url, verify=False)
                    if r.status_code == STATUS_CODE_200:
                        content = r.content.decode('utf-8')
                        layer_info = json.loads(content)
                        layer_load_status_string = layer_info["loadStatus"]
                        lyr['loadStatus'] = layer_load_status_string
                        if layer_load_status_string != 'Loaded': 
                            # if failed to load
                            if "errorMessage" in layer_info:
                                layer_error_message_string = layer_info["errorMessage"]
                                lyr['errorMessage'] = layer_error_message_string
                        else:
                            # if loaded sucessfully
                            if     rlt == rlt_error_6\
                                or rlt == rlt_error_7:
                                lyr['passTestResult'] = True
                            else:
                                lyr['passTestResult'] = False 
                    else:
                        lyr[get_layer_status_code_field] = r.status_code
                        lyr['passTestResult'] = False 
                else:
                    lyr['passTestResult'] = False 

                    lyr[get_layer_status_code_field] = r.status_code
                result_array.append(lyr)

            save_testcases_json(result_array, neg_get_added_layer_result_json_path)
                
    def test_add_layers_pos_cases(self):

        safe_delete_file(positive_addlayer_notpass_json_path)

        # the layer id file exist, we don't load it again
        if not os.path.exists(pos_add_layer_result_json_path):
            print("Start Step 1: Add layer")
            self.test_add_layers_pos_cases_step1()
            time.sleep(sleep_time_after_add_pos_layer)
        else:
            print("Skip Step 1: Add layer")

        print("Start Step 2: Get layer")
        all_passed = self.pos_get_added_layer()

        print("Start Step 3: Verfiy result")
        all_passed = self.pos_verfiy_get_layer_result()

        # remove this file, so next time we can run again
        if all_passed is True:
            safe_delete_file(pos_add_layer_result_json_path)
            delete_all_layers()


        
    def test_add_layers_neg_cases(self):

        safe_delete_file(negative_addlayer_notpass_json_path)

        # the layer id file exist, we don't load it again
        if not os.path.exists(neg_add_layer_result_json_path):
            print("Start Step 1: Add layer")
            self.test_add_layers_neg_cases_step1()
            time.sleep(sleep_time_after_add_neg_layer)
        else:
            print("Skip Step 1: Add layer")

        print("Start Step 2: Get layer")
        self.neg_get_added_layer()

        print("Start Step 3: Verfiy result")
        all_passed = self.neg_verfiy_get_layer_result()

        # remove this file, so next time we can run again
        if all_passed is True:
            safe_delete_file(neg_add_layer_result_json_path)
            delete_all_layers()


    def pos_verfiy_get_layer_result(self):

        add_layer_notpass_cases = load_test_cases(positive_addlayer_notpass_json_path)
        get_added_layer_rlt_array = load_test_cases(pos_get_added_layer_result_json_path)
        for r in get_added_layer_rlt_array:
            if (not 'passTestResult' in r) or (r['passTestResult']) == False:
                add_layer_notpass_cases.append(r)

        save_testcases_json(add_layer_notpass_cases, positive_addlayer_notpass_json_path)
        if len(add_layer_notpass_cases) == 0:
            print("Test sucessed! All positive testcases for adding layer passed!")
        else:
            print("Test failed! More details please view {}".format(positive_addlayer_notpass_json_path))
        return len(add_layer_notpass_cases) == 0

    
    def neg_verfiy_get_layer_result(self):
        add_layer_notpass_cases = load_test_cases(negative_addlayer_notpass_json_path)
        get_added_layer_rlt_array = load_test_cases(neg_get_added_layer_result_json_path)
        for r in get_added_layer_rlt_array:
            if (not 'passTestResult' in r) or (r['passTestResult']) == False:
                add_layer_notpass_cases.append(r)
        save_testcases_json(add_layer_notpass_cases, negative_addlayer_notpass_json_path)
        if len(add_layer_notpass_cases) == 0:
            print("Test sucessed! All negative testcases for adding layer passed!")
        else:
            print("Test failed! More details please view {}".format(negative_addlayer_notpass_json_path))
        return len(add_layer_notpass_cases) == 0


def run_common_unit_test():
    csv_url_0 = "../Data/AutomationAPI/AddLayer/TestingLayers_Previous.csv"
    csv_url_1 = "../Data/AutomationAPI/AddLayer/TestCases_1.11.csv"
    csv_url_3 = "../Data/AutomationAPI/AddLayer/quick_test.csv"

    csv_url_0 = convert_to_absolute_path(csv_url_0)
    csv_url_1 = convert_to_absolute_path(csv_url_1)
    csv_url_3 = convert_to_absolute_path(csv_url_3)

    test = EarthAutomationAPILayerTest([csv_url_0, csv_url_1])
    #test = EarthAutomationAPILayerTest([csv_url_3])

    test.test_add_layers_pos_cases()
    test.test_add_layers_neg_cases()


if __name__ == '__main__':
    run_common_unit_test()


