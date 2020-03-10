'''
***************
Name:Sunny
Time:2020/2/25
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
from library.Colour import color
from common.handle_data import CaseData


@ddt
class TestLogin(unittest.TestCase):
    excel = Readexcel(os.path.join(data_dir, "api_cases_excel.xlsx"), "login")
    cases = excel.read_data()
    send = HandleRequests()

    @data(*cases)
    def test_login(self, case):
        # 准备用例数据
        url = conf.get("env", "url") + case["url"]
        data = eval(case["data"])
        headers = eval(conf.get("env", "headers"))
        method = case["method"]
        expected = eval(case["expected"])
        row = case["case_id"] + 1

        # 发送请求
        reponse = self.send.send_requests(url=url, method=method, headers=headers, json=data)
        res = reponse.json()

        # 断言
        try:
            self.assertEqual(expected["code"], res["code"])
            self.assertEqual(expected["msg"], res["msg"])
        except AssertionError as e:
            self.excel.write_data(row=row, column=8, value="不通过")
            log.error("用例：{} ，执行".format(case["title"]) + color.white_red("不通过"))
            log.exception(e)
            raise e
        else:
            self.excel.write_data(row=row, column=8, value="通过")
            log.info("用例：{} ，执行".format(case["title"]) + color.white_green("通过"))


@ddt
class TestRegister(unittest.TestCase):
    excel = Readexcel(os.path.join(data_dir, "api_cases_excel.xlsx"), "register")
    cases = excel.read_data()
    send = HandleRequests()
    basedata = HandleDB()

    @data(*cases)
    def test_register(self, case):
        # 准备用例数据
        url = conf.get("env", "url") + case["url"]
        headers = eval(conf.get("env", "headers"))
        case["data"] = case["data"].replace("#phone#",self.randam_phone())
        data = eval(case["data"])
        method = case["method"]
        expected = eval(case["expected"])
        row = case["case_id"] + 1

        # 发送请求
        response = self.send.send_requests(method=method, url=url, json=data, headers=headers)
        res = response.json()
        id = jsonpath.jsonpath(res, "$..id")
        # 读取数据库的数据
        sql = "select * from futureloan.member where mobile_phone = {}".format(self.randam_phone())
        sql_data = self.basedata.find_all(sql)
        # 断言
        try:
            self.assertEqual(expected["code"], res["code"])
            self.assertEqual(expected["msg"], res["msg"])
            if expected["code"] == 0:
                for i in sql_data:
                    bd_phone = i["mobile_phone"]
                    bd_type = i["type"]
                    bd_reg_name = i["reg_name"]
                    bd_id = i["id"]
                    self.assertEqual(expected["mobile_phone"], bd_phone)
                    self.assertEqual(expected["type"], bd_type)
                    self.assertEqual(expected["reg_name"], bd_reg_name)
                    self.assertEqual(0, i["leave_amount"])
                    self.assertEqual(id, bd_id)

        except AssertionError as e:
            self.excel.write_data(row=row, column=8, value="不通过")
            log.error("用例：{} ，执行".format(case["title"]) + color.white_red("不通过"))
            log.exception(e)
            raise e
        else:
            print("预期结果：", expected)
            print("实际结果：", res)
            self.excel.write_data(row=row, column=8, value="通过")
            log.info("用例：{} ，执行".format(case["title"]) + color.white_green("通过"))

    def randam_phone(self):
        phone = "133"
        for i in range(8):
            num = random.randint(1, 9)
            phone += str(num)
        return phone


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
        cls.token_value = token_type + " " + token
        cls.member_id = jsonpath.jsonpath(data, "$..id")[0]

    @data(*cases)
    def test_recharge(self, case):
        # 准备用例数据
        url = conf.get("env", "url") + case["url"]
        headers = eval(conf.get("env", "headers"))
        headers["Authorization"] = self.token_value
        case["data"] = case["data"].replace("#member_id#", str(self.member_id))
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
            print("实际结果：,", res)
            self.excel.write_data(row=row, column=8, value="不通过")
            log.error("用例：{} ，执行".format(case["title"]) + color.white_red("不通过"))
            log.exception(e)
            raise e
        else:
            self.excel.write_data(row=row, column=8, value="通过")
            log.info("用例：{} ，执行".format(case["title"]) + color.white_green("通过"))


@ddt
class TestWithdraw(unittest.TestCase):
    execl = Readexcel(os.path.join(data_dir, "api_cases_excel.xlsx"), "withdraw")
    cases = execl.read_data()
    request = HandleRequests()
    basedata = HandleDB()

    @classmethod
    def setUpClass(cls):
        # 准备参数
        url = conf.get("env", "url") + "/member/login"
        data = {
            "mobile_phone": conf.get("test_case", "mobile_phone"),
            "pwd": conf.get("test_case", "pwd")
        }
        headers = eval(conf.get("env", "headers"))
        method = "post"
        # 发送请求
        response = cls.request.send_requests(method=method, url=url, json=data, headers=headers)
        data = response.json()
        token_type = jsonpath.jsonpath(data, "$..token_type")[0]
        token = jsonpath.jsonpath(data, "$..token")[0]
        cls.token_value = token_type + " " + token
        cls.member_id = jsonpath.jsonpath(data, "$..id")[0]

    @data(*cases)
    def test_withdraw(self, case):
        # 准备用例数据
        url = conf.get("env", "url") + case["url"]
        case["data"] = case["data"].replace("#member_id#", str(self.member_id))
        data = eval(case["data"])
        headers = eval(conf.get("env", "headers"))
        headers["Authorization"] = self.token_value
        method = case["method"]
        expected = eval(case["expected"])
        row = case["case_id"] + 1
        # 发送请求前的金额
        sql = "select leave_amount from futureloan.member where mobile_phone = {}".format(
            conf.get("test_case", "mobile_phone"))
        pre_money = self.basedata.find_one(sql=sql)["leave_amount"]
        # 发送请求
        response = self.request.send_requests(method=method, url=url, json=data, headers=headers)
        res = response.json()
        # 断言
        try:
            self.assertEqual(expected["code"], res["code"])
            self.assertEqual(expected["msg"], res["msg"])
            if expected["code"] == 0:
                end_money = self.basedata.find_one(sql=sql)["leave_amount"]
                self.assertEqual(pre_money-end_money,Decimal(str(data["amount"])))

        except AssertionError as e:
            print("预期结果：",expected)
            print("实际结果：",res)
            self.execl.write_data(row=row, column=8, value="未通过")
            log.error("用例：{} ，执行".format(case["title"]) + color.white_red("未通过"))
            log.exception(e)
            raise e
        else:
            self.execl.write_data(row=row, column=8, value="通过")
            log.info("用例：{}，执行".format(case["title"]) + color.white_green("通过"))
