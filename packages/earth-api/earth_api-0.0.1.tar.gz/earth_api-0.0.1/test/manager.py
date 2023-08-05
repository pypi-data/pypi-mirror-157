import os
import sys

expr_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../'))

if  expr_path not in sys.path:
    sys.path.insert(0, expr_path)


from test.test_addlayer_latest import run as run_test_addlayer_latest 
from test.test_add_graphic import run_automatic_test as run_automatic_test_test_add_graphic
from test.test_patch_graphic import run_automatic_test as run_automatic_test_test_patch_graphic
from test.run_all_v1_api_test import run as run_run_all_v1_api_test
from test.run_all_latest_api_test import run as run_run_all_latest_api_test

def add_layer(task_name="task_v_latest.json"):
    run_test_addlayer_latest(task_name)

def add_graphic():
    run_automatic_test_test_add_graphic()

def patch_graphic():
    run_automatic_test_test_patch_graphic()

def all_v1_api():
    run_run_all_v1_api_test()

def all_latest_api():
    run_run_all_latest_api_test()

if __name__ == '__main__':
    import fire
    fire.Fire()
