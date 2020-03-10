'''
***************
Name:Sunny
Time:2020/2/27
***************
'''
import unittest
import os
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


@ddt
class TestWithdraw(unittest.TestCase):
    excel = Readexcel(os.path.join(data_dir, "api_cases_excel.xlsx"), "tixian")
    cases = excel.read_data()
    request = HandleRequests()
    basedata = HandleDB()

    @data(*cases)
    def test_withdraw(self, case):
        # 准备用例数据
        url = conf.get("env", "url") + case["url"]
        headers = eval(conf.get("env", "headers"))
        case["data"] = CaseData.replace_data(case["data"])
        if case["interface"] == "withdraw":
            headers["Authorization"] = getattr(CaseData,"token_value")
        data = eval(case["data"])
        expected = eval(case["expected"])
        method = case["method"]
        row = case["case_id"] + 1
        # 发送请求
        # 发送请求前查询数据库leave_amount金额
        if expected["code"] == 0:
            sql = "select leave_amount from futureloan.member where mobile_phone = {}".format(
                conf.get("test_case", "mobile_phone"))
            start_money = self.basedata.find_one(sql)["leave_amount"]
        reponse = self.request.send_requests(method=method, url=url, json=data, headers=headers)
        res = reponse.json()
        # 执行登录用例后，提取返回的token和member_id
        if case["interface"] == "login":
            token_type = jsonpath.jsonpath(res, "$..token_type")[0]
            token = jsonpath.jsonpath(res, "$..token")[0]
            CaseData.token_value = token_type + " " + token
            CaseData.member_id = str(jsonpath.jsonpath(res, "$..id")[0])
        # 断言
        try:
            self.assertEqual(expected["code"], res["code"])
            self.assertEqual(expected["msg"], res["msg"])
            if expected["code"] == 0 and case["interface"] != "login":
                sql = "select leave_amount from futureloan.member where mobile_phone = {}".format(
                    conf.get("test_case", "mobile_phone"))
                end_money = self.basedata.find_one(sql)["leave_amount"]
                self.assertEqual(start_money-end_money,Decimal(str(data["amount"])))

        except AssertionError as e:
            print("预期结果：",expected)
            print("实际结果：",res)
            self.excel.write_data(row=row, column=8, value="不通过")
            log.error("用例：{} 执行未通过".format(case["title"]))
            log.exception(e)
            raise e
        else:
            self.excel.write_data(row=row, column=8, value="通过")
            log.info("用例：{} 执行通过".format(case["title"]))
