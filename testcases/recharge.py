'''
***************
Name:Sunny
Time:2020/2/29
***************
'''
import unittest
import os
import random
import jsonpath
from decimal import Decimal
from library.ddt import ddt, data
from common.readexcel import Readexcel
from common.handlepath import data_dir
from common.handleconfig import conf
from common.handlerequests import HandleRequests
from common.handlelog import log
from common.handlemysql import HandleDB
from common.handle_data import CaseData
from library.Colour import color




@ddt
class TestRecharge(unittest.TestCase):
    excel = Readexcel(os.path.join(data_dir, "api_cases_excel.xlsx"), "recharge")
    cases = excel.read_data()
    send = HandleRequests()
    basedata = HandleDB()

    @classmethod
    def setUpClass(cls):
        url = conf.get("env", "url") + "/member/login"
        data = {
            "mobile_phone": conf.get("test_case", "mobile_phone"),
            "pwd": conf.get("test_case", "pwd")
        }
        headers = eval(conf.get("env", "headers"))
        method = "post"
        login_response = cls.send.send_requests(url=url, method=method, headers=headers, json=data)
        data = login_response.json()
        token_type = jsonpath.jsonpath(data, "$..token_type")[0]
        token = jsonpath.jsonpath(data, "$..token")[0]
        CaseData.token_value = token_type + " " + token
        CaseData.member_id = str(jsonpath.jsonpath(data, "$..id")[0])

    @data(*cases)
    def test_recharge(self, case):
        # 准备用例数据
        url = conf.get("env", "url") + case["url"]
        headers = eval(conf.get("env", "headers"))
        headers["Authorization"] = getattr(CaseData,"token_value")
        case["data"] = CaseData.replace_data(case["data"])
        data = eval(case["data"])
        method = case["method"]
        expected = eval(case["expected"])
        row = case["case_id"] + 1
        # 发送请求
        if eval(case["expected"])["code"] == 0:
            sql = "select leave_amount from futureloan.member where mobile_phone={}".format(
                conf.get("test_case", "mobile_phone"))
            pre_data = self.basedata.find_one(sql)["leave_amount"]

        response = self.send.send_requests(method=method, url=url, json=data, headers=headers)
        res = response.json()
        # 断言
        try:
            self.assertEqual(expected["code"], res["code"])
            self.assertEqual(expected["msg"], res["msg"])
            if expected["code"] == 0:
                end_data = self.basedata.find_one(sql)["leave_amount"]
                self.assertEqual(Decimal(str(data["amount"])), end_data - pre_data)
        except AssertionError as e:
            print("预期结果：", expected)
            print("实际结果：", res)
            self.excel.write_data(row=row, column=8, value="不通过")
            log.error("用例：{} ，执行".format(case["title"]) + color.white_red("不通过"))
            log.exception(e)
            raise e
        else:
            self.excel.write_data(row=row, column=8, value="通过")
            log.info("用例：{} ，执行".format(case["title"]) + color.white_green("通过"))