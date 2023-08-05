# -*- coding:utf-8 -*-
import os
import sys
expr_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../'))

if  expr_path not in sys.path:
    sys.path.insert(0, expr_path)

import unittest
import time
from test.HTMLTestRunner import HTMLTestRunner

# case_path = os.path.join(os.getcwd())
# 用例路径
case_path = os.path.dirname(__file__)
# 报告存放路径
report_path = os.path.join(os.path.dirname(__file__), '../Data/AutomationAPI/report')
if not os.path.exists(report_path):
    os.mkdir(report_path)

def all_case():
    discover = unittest.defaultTestLoader.discover(case_path, pattern="test*api.py", top_level_dir=None)
    return discover

def run():
    # 1、获取当前时间，这样便于下面的使用。
    now = time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime(time.time()))

    # 2、html报告文件路径
    report_abspath = os.path.abspath(os.path.join(report_path, "result_"+now+".html"))

    # 3、打开一个文件，将result写入此file中
    fp = open(report_abspath, "wb")
    runner = HTMLTestRunner(stream=fp,
                            title='Automatic Test for EARTH Automation API 1.16:',
                            description='Result:')
    # 4、调用add_case函数返回值
    runner.run(all_case())
    fp.close()
    print("More details: {}".format(report_abspath))
    os.system("start explorer %s" % f'{report_abspath}')



if __name__ == '__main__':
    run()
