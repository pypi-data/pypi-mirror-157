from __future__ import absolute_import

import requests
import ssl
import json
import time
import csv
import os
import sys
import logging

expr_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../'))

if  expr_path not in sys.path:
    sys.path.insert(0, expr_path)


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
api_version_latest = "?api-version=latest"
layer_endpoint = "/layer"
layers_endpoint = "/layers"

add_layer_status_code_field = "addLyrStatusCode"
get_layer_status_code_field = "getLyrStatusCode"


# -- Root
# ---- bin
# ---- Data
# ------ AutomationAPI 
# -------- AddLayer

ADDLAYER_DATA_RELATIVE_FOLDER_PATH = "../Data/AutomationAPI/AddLayer"
REPORT_RELATIVE_FOLDER_PATH = "../Data/AutomationAPI/report"



def get_addlayer_data_folder():
    current_path = os.path.dirname(__file__)
    return os.path.abspath(os.path.join(current_path, ADDLAYER_DATA_RELATIVE_FOLDER_PATH))

def get_report_folder(): 
    current_path = os.path.dirname(__file__)
    return os.path.abspath(os.path.join(current_path, REPORT_RELATIVE_FOLDER_PATH))


def get_absolute_path_from_name(file_name):
    folder = get_addlayer_data_folder()
    if not os.path.exists(folder):
        raise ("{} not exists!".format(folder))
    return os.path.abspath(os.path.join(folder, file_name))

def get_absolute_report_file_path_from_name(file_name):
    folder = get_report_folder()
    if not os.path.exists(folder):
        raise ("{} not exists!".format(folder))
    return os.path.abspath(os.path.join(folder, file_name))

def convert_to_absolute_path(rel_path):
    current_path = os.path.dirname(__file__)
    return os.path.abspath(os.path.join(current_path, rel_path))

FILE_NAME_FIELD = "fileNames"
RUN_POSITIVE_CASES_FIELD = "runPositiveCases"
RUN_NEGATIVE_CASES_FIELD = "runNegativeCases"

POS_TESTCASES_JSON_PATH_POSTFIX = "_positive_testcases"
NEG_TESTCASES_JSON_PATH_POSTFIX = "_negative_testcases"

NEG_ADD_LAYER_RESULT_JSON_PATH_POSTFIX = "_negative_add_layer_result"
POS_ADD_LAYER_RESULT_JSON_PATH_POSTFIX = "_positive_add_layer_result"

POS_GET_ADDED_LAYER_RESULT_JSON_PATH_POSTFIX = "_positive_get_added_layer_result"
NEG_GET_ADDED_LAYER_RESULT_JSON_PATH_POSTFIX = "_negative_get_added_layer_result"

POSITIVE_ADDLAYER_NOTPASS_JSON_PATH_POSTFIX = "_positive_not_pass"
NEGATIVE_ADDLAYER_NOTPASS_JSON_PATH_POSTFIX = "_negative_not_pass"

ADDLAYER_RESULT_JSON_PATH_POSTFIX = "_addlayer_result"

addlayer_log_path = get_absolute_report_file_path_from_name("addlayer.log")

# https://blog.csdn.net/qq_40558166/article/details/107759034
# https://blog.csdn.net/Chelseady/article/details/100216882
logging.basicConfig(
    format="%(asctime)s %(name)s:%(levelname)s:%(message)s", 
    datefmt="%d-%M-%Y %H:%M:%S", 
    filename=addlayer_log_path,
    level=logging.DEBUG
)

def get_json_report_path(testcase_path, postfix):
    basename = os.path.basename(testcase_path)
    title = basename.split(".")[0]
    title = title + postfix
    basename = title + ".json"
    relative_path = "../Data/AutomationAPI/report/" + basename
    abs_path = convert_to_absolute_path(relative_path)
    return abs_path


disable_error_type_2 = True 
sleep_time_after_add_neg_layer = 20 # unit seconds
sleep_time_after_add_pos_layer = 40 # unit seconds, as we change the add layer logic
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



def get_lyr_json(lyr):
    return json.dumps(lyr)


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
    logging.info("Total cases:{}\n Positive cases:{}\n Negative cases:{}\n".format(num_all_cases, num_pos_cases, num_neg_cases))
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
    url = base_address + layers_endpoint + "/AllLayers" + api_version_latest
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



class TestcasesGroup:
    """ one group one csv
    """
    def __init__(self, csv_path):
        self.csv_path = csv_path

        self.pos_testcases_json_path                = get_json_report_path(self.csv_path, POS_TESTCASES_JSON_PATH_POSTFIX)
        self.neg_testcases_json_path                = get_json_report_path(self.csv_path, NEG_TESTCASES_JSON_PATH_POSTFIX)
        self.neg_add_layer_result_json_path         = get_json_report_path(self.csv_path, NEG_ADD_LAYER_RESULT_JSON_PATH_POSTFIX) 
        self.pos_add_layer_result_json_path         = get_json_report_path(self.csv_path, POS_ADD_LAYER_RESULT_JSON_PATH_POSTFIX)
        self.neg_get_added_layer_result_json_path   = get_json_report_path(self.csv_path, NEG_GET_ADDED_LAYER_RESULT_JSON_PATH_POSTFIX)
        self.pos_get_added_layer_result_json_path   = get_json_report_path(self.csv_path, POS_GET_ADDED_LAYER_RESULT_JSON_PATH_POSTFIX)
        self.negative_addlayer_notpass_json_path    = get_json_report_path(self.csv_path, NEGATIVE_ADDLAYER_NOTPASS_JSON_PATH_POSTFIX)
        self.positive_addlayer_notpass_json_path    = get_json_report_path(self.csv_path, POSITIVE_ADDLAYER_NOTPASS_JSON_PATH_POSTFIX)

        self.pos_cases, self.neg_cases = generate_testcases([csv_path])

        save_testcases_json(self.pos_cases, self.pos_testcases_json_path)
        save_testcases_json(self.neg_cases, self.neg_testcases_json_path)
        self.error_message = []


    def test_add_layers_pos_cases_step1(self):
        not_passed_cases = []
        url = base_address + layer_endpoint +  api_version_latest
        layer_array = []
        for case in self.pos_cases:
            time.sleep(1)
            cid = case['cid']
            lyr = case['lyr']
            layer_id = None
            layer_json_str = get_lyr_json(lyr)
            headers = {"content-Type": "application/json"}

            exception = False 
            try:
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
                                logging.error("No.{} Failed!".format(cid))
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
                        logging.info("No.{} Status Code: {}".format(cid, r.status_code))
                        layer_array.append(case)
                    time.sleep(sleep_time_between_add_pos_layer)
            except Exception as e:
                logging.error("{}".format(e))
                self.error_message.append("{}".format(e))
                exception = True

                if exception is True or (r.status_code != STATUS_CODE_200 and r.status_code != STATUS_CODE_500):
                    print("No.{} Failed!".format(cid))
                    logging.error("No.{} Failed!".format(cid))
                    not_passed_cases.append(case)
            

        save_testcases_json(not_passed_cases, self.positive_addlayer_notpass_json_path)
        save_testcases_json(layer_array, self.pos_add_layer_result_json_path)


    def test_add_layers_neg_cases_step1(self):
        not_passed_cases = []
        url = base_address + layer_endpoint +  api_version_latest
        layer_array = []
        for case in self.neg_cases:
            cid = case['cid']
            lyr = case['lyr']
            layer_id = None
            layer_json_str = get_lyr_json(lyr)            
            headers = {"content-Type": "application/json"}
            r = requests.post(url, data=layer_json_str,
                            headers=headers, verify=False)
            if r.status_code == STATUS_CODE_200 or r.status_code == STATUS_CODE_500:
                content = r.content.decode('utf-8')
                if content != '':
                    results = json.loads(content)
                    if r.status_code == STATUS_CODE_200 and "id" in results:
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
                    logging.info("No.{} Status Code: {}".format(cid, r.status_code))
                    layer_array.append(case)
            else:
                print("No.{} Failed!".format(cid))
                logging.error("No.{} Failed!".format(cid))
                not_passed_cases.append(case)

        save_testcases_json(not_passed_cases, self.negative_addlayer_notpass_json_path)
        save_testcases_json(layer_array, self.neg_add_layer_result_json_path)


    def pos_get_added_layer(self):
        all_passed = True 
        layer_array = None
        with open(self.pos_add_layer_result_json_path, 'r') as jf:
            layer_array = json.loads(jf.read())
            result_array = []
        if len(layer_array) > 0:
            for layer in layer_array:
                lyr = layer.copy()
                status_code = lyr[add_layer_status_code_field]
                passTest = False
                if status_code == STATUS_CODE_200:
                    url = base_address + layer_endpoint + "/" + lyr['lid'] + api_version_latest
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
                logging.info("Cid:{} Passed:{}".format(lyr['cid'], passTest))
                result_array.append(lyr)
            save_testcases_json(result_array, self.pos_get_added_layer_result_json_path)
            return all_passed


    def neg_get_added_layer(self):
        layer_array = None
        with open(self.neg_add_layer_result_json_path, 'r') as jf:
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
                elif status_code == STATUS_CODE_200 and lyr['lid'] is None:
                    # just for some cases in geopackage
                    if rlt == rlt_error_6 or rlt == rlt_error_7 or rlt == rlt_error_3:
                        lyr['passTestResult'] = True
                elif status_code == STATUS_CODE_200 and lyr['lid'] is not None:
                    url = base_address + layer_endpoint + "/" + lyr['lid'] + api_version_latest
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
                    #lyr[get_layer_status_code_field] = r.status_code
                result_array.append(lyr)

            save_testcases_json(result_array, self.neg_get_added_layer_result_json_path)

                
    def test_add_layers_pos_cases(self):
        print("Start run pos cases in {}.\n".format(self.csv_path))
        logging.info("Start run pos cases in {}.\n".format(self.csv_path))

        safe_delete_file(self.positive_addlayer_notpass_json_path)

        # the layer id file exist, we don't load it again
        if not os.path.exists(self.pos_add_layer_result_json_path):
            print("Start Step 1: Add layer")
            logging.info("Start Step 1: Add layer")
            self.test_add_layers_pos_cases_step1()
            time.sleep(sleep_time_after_add_pos_layer)
            print("\nSleep {} seconds after add pos testcases.\n".format(sleep_time_after_add_pos_layer))
            logging.info("\nSleep {} seconds after add pos testcases.\n".format(sleep_time_after_add_pos_layer))
        else:
            print("Skip Step 1: Add layer")
            logging.info("Skip Step 1: Add layer")

        print("Start Step 2: Get layer")
        logging.info("Start Step 2: Get layer")
        all_passed = self.pos_get_added_layer()

        print("Start Step 3: Verfiy result")
        logging.info("Start Step 3: Verfiy result")
        all_passed = self.pos_verfiy_get_layer_result()

        # remove this file, so next time we can run again
        if all_passed is True:
            safe_delete_file(self.pos_add_layer_result_json_path)
            delete_all_layers()


        
    def test_add_layers_neg_cases(self):
        print("Start run neg cases in {}.\n".format(self.csv_path))
        logging.info("Start run neg cases in {}.\n".format(self.csv_path))

        safe_delete_file(self.negative_addlayer_notpass_json_path)

        # the layer id file exist, we don't load it again
        if not os.path.exists(self.neg_add_layer_result_json_path):
            print("Start Step 1: Add layer")
            logging.info("Start Step 1: Add layer")
            self.test_add_layers_neg_cases_step1()
            time.sleep(sleep_time_after_add_neg_layer)
            print("\nSleep {} seconds after add neg testcases.\n".format(sleep_time_after_add_neg_layer))
            logging.info("\nSleep {} seconds after add neg testcases.\n".format(sleep_time_after_add_neg_layer))
        else:
            print("Skip Step 1: Add layer")
            logging.info("Skip Step 1: Add layer")

        print("Start Step 2: Get layer")
        logging.info("Start Step 2: Get layer")
        self.neg_get_added_layer()

        print("Start Step 3: Verfiy result")
        logging.info("Start Step 3: Verfiy result")
        all_passed = self.neg_verfiy_get_layer_result()

        # remove this file, so next time we can run again
        if all_passed is True:
            safe_delete_file(self.neg_add_layer_result_json_path)
            delete_all_layers()


    def pos_verfiy_get_layer_result(self):

        add_layer_notpass_cases = load_test_cases(self.positive_addlayer_notpass_json_path)
        get_added_layer_rlt_array = load_test_cases(self.pos_get_added_layer_result_json_path)
        for r in get_added_layer_rlt_array:
            if (not 'passTestResult' in r) or (r['passTestResult']) == False:
                add_layer_notpass_cases.append(r)

        save_testcases_json(add_layer_notpass_cases, self.positive_addlayer_notpass_json_path)
        if len(add_layer_notpass_cases) == 0:
            print("Test sucessed! All positive testcases for adding layer passed!\n")
            logging.info("Test sucessed! All positive testcases for adding layer passed!\n")
        else:
            error = "Test failed! More details please view {}.\n".format(self.positive_addlayer_notpass_json_path) 
            self.error_message.append(error)
            logging.error(error)
        return len(add_layer_notpass_cases) == 0

    
    def neg_verfiy_get_layer_result(self):
        add_layer_notpass_cases = load_test_cases(self.negative_addlayer_notpass_json_path)
        get_added_layer_rlt_array = load_test_cases(self.neg_get_added_layer_result_json_path)
        for r in get_added_layer_rlt_array:
            if (not 'passTestResult' in r) or (r['passTestResult']) == False:
                add_layer_notpass_cases.append(r)
        save_testcases_json(add_layer_notpass_cases, self.negative_addlayer_notpass_json_path)
        if len(add_layer_notpass_cases) == 0:
            print("Test sucessed! All negative testcases for adding layer passed!\n")
            logging.info("Test sucessed! All negative testcases for adding layer passed!\n")
        else:
            error = "Test failed! More details please view {}.\n".format(self.negative_addlayer_notpass_json_path) 
            self.error_message.append(error)
            print(error)
            logging.error(error)

        return len(add_layer_notpass_cases) == 0


# need follow the order
class EarthAutomationAPILayerTest:

    def __init__(self, csv_paths=None, task_name=None):

        self.ts_group_array = []

        self.task_path = get_absolute_path_from_name(task_name) 

        if self.task_path is not None:
            self.addlayer_result_json_path = get_json_report_path(self.task_path, ADDLAYER_RESULT_JSON_PATH_POSTFIX)
        else:
            self.addlayer_result_json_path = None


        if csv_paths is not None and len(csv_paths) > 0:
            for csv_path in csv_paths:
                ts_group = TestcasesGroup(csv_path)
                self.ts_group_array.append(ts_group)
        

    def run_addlayer_pos_cases(self):
        for ts_group in self.ts_group_array:
            ts_group.test_add_layers_pos_cases()


    def run_addlayer_neg_cases(self):
        for ts_group in self.ts_group_array:
            ts_group.test_add_layers_neg_cases()
    
    def print_error_message(self):
        result = []
        msg = "Not all testcases passed!"
        has_error = False
        for ts_group in self.ts_group_array:
            for error in ts_group.error_message:
                has_error = True
                result.append(error)
                print(error)
                logging.error(error)

        if has_error is False:
            msg = "All tests about adding layer passed!"

        print(msg)
        logging.info(msg)
        
        if self.addlayer_result_json_path is not None:
            rlt_dict = {
                "msg" :msg,
                "details" : result
            }
            save_testcases_json(rlt_dict, self.addlayer_result_json_path)
        


def run_common_unit_test():
    csv_url_0 = "../Data/AutomationAPI/AddLayer/TestingLayers_Previous.csv"
    csv_url_1 = "../Data/AutomationAPI/AddLayer/TestCases_1.11.csv"
    csv_url_3 = "../Data/AutomationAPI/AddLayer/quick_test.csv"

    csv_url_0 = convert_to_absolute_path(csv_url_0)
    csv_url_1 = convert_to_absolute_path(csv_url_1)
    csv_url_3 = convert_to_absolute_path(csv_url_3)

    csv_array = [
        "../Data/AutomationAPI/AddLayer/TestCases_1_11_part1.csv",
        "../Data/AutomationAPI/AddLayer/TestCases_1_11_part2.csv",
        "../Data/AutomationAPI/AddLayer/TestCases_1_11_part3.csv",
        "../Data/AutomationAPI/AddLayer/TestingLayers_Previous_part1.csv",
        "../Data/AutomationAPI/AddLayer/TestingLayers_Previous_part2.csv",
        "../Data/AutomationAPI/AddLayer/TestingLayers_Previous_part3.csv",
        "../Data/AutomationAPI/AddLayer/TestingLayers_Previous_part4.csv"
    ]

    for i in range(len(csv_array)):
        csv_array[i] = convert_to_absolute_path(csv_array[i])

    test = EarthAutomationAPILayerTest(csv_array)

    test.run_addlayer_pos_cases()
    test.run_addlayer_neg_cases()
    test.print_error_message()


def __get_task_details(task_file_name):
    task_path = get_absolute_path_from_name(task_file_name)

    if not os.path.exists(task_path):
        raise("Task path: {} not exits!".format(task_path))

    task = json.load(open(task_path, 'r'))

    if FILE_NAME_FIELD not in task:
        raise ("Missing {} field".format(FILE_NAME_FIELD))
    
    csv_names = task[FILE_NAME_FIELD]
    csv_array = [get_absolute_path_from_name(csv) for csv in csv_names]

    b_run_pos = True
    b_run_neg = True

    if RUN_POSITIVE_CASES_FIELD in task:
        b_run_pos = task[RUN_POSITIVE_CASES_FIELD]

    if RUN_NEGATIVE_CASES_FIELD in task:
        b_run_neg = task[RUN_NEGATIVE_CASES_FIELD]

    return csv_array, b_run_pos, b_run_neg 



def run(task_file_name="task_v_latest.json"):
    csv_array, b_run_pos, b_run_neg = __get_task_details(task_file_name)
    test = EarthAutomationAPILayerTest(csv_array, task_file_name)

    if b_run_pos is True:
        test.run_addlayer_pos_cases()
    if b_run_neg is True:
        test.run_addlayer_neg_cases()
    if b_run_pos is False and b_run_neg is False:
        raise("Check fields {} and {}.".format(RUN_POSITIVE_CASES_FIELD, RUN_NEGATIVE_CASES_FIELD))
    test.print_error_message()


if __name__ == '__main__':
    #run_common_unit_test()
    run()


