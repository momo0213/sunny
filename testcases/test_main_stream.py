'''
***************
Name:Sunny
Time:2020/3/6
***************
'''
import unittest
import os
import random
import jsonpath
from library.ddt import ddt, data
from common.readexcel import Readexcel
from common.handlepath import data_dir
from common.handleconfig import conf
from common.handlerequests import HandleRequests
from common.handlelog import log
from common.handle_data import CaseData


@ddt
class TestMainStream(unittest.TestCase):
    excel = Readexcel(os.path.join(data_dir, "api_cases_excel.xlsx"), "main_stream")
    cases = excel.read_data()
    request = HandleRequests()

    @data(*cases)
    def test_main_stream(self, case):
        # 准备用例数据
        url = conf.get("env", "url") + CaseData.replace_data(case["url"])
        headers = eval(conf.get("env", "headers"))
        if case["interface"] != "login" and case["interface"] != "register":
            headers["Authorization"] = getattr(CaseData, "token_value")
        if case["interface"] == "register":
            CaseData.mobilephone = self.random_phone()
        case["data"] = str(CaseData.replace_data(case["data"]))
        data = eval(case["data"])
        method = case["method"]
        expected = eval(case["expected"])
        row = case["case_id"] + 1
        # 发送请求并获取结果
        response = self.request.send_requests(url=url, method=method, headers=headers, json=data)
        res = response.json()
        print("预期结果:",expected)
        print("实际结果:",res)
        # 登录后提取token和member_id并保存为类属性
        if case["interface"] == "login":
            token_type = jsonpath.jsonpath(res, "$..token_type")[0]
            token = jsonpath.jsonpath(res, "$..token")[0]
            CaseData.token_value = token_type + " " + token
            CaseData.member_id = str(jsonpath.jsonpath(res, "$..id")[0])
        # 加标后提取项目id并保存为类属性
        if case["interface"] == "add":
            CaseData.loan_id = str(jsonpath.jsonpath(res, "$..id")[0])

        # 断言
        try:
            self.assertEqual(expected["code"], res["code"])
            self.assertEqual(expected["msg"], res["msg"])
        except AssertionError as e:
            self.excel.write_data(row=row, column=8, value="不通过")
            log.error("用例:{} 执行不通过".format(case["title"]))
            log.exception(e)
            raise e
        else:
            self.excel.write_data(row=row, column=8, value="通过")
            log.info("用例:{} 执行通过".format(case["title"]))

    def random_phone(self):
        phone = "130"
        for i in range(8):
            num = random.randint(1, 9)
            phone += str(num)
        return phone
