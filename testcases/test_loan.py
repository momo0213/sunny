'''
***************
Name:Sunny
Time:2020/2/28
***************
'''
import unittest
import os
import jsonpath
from common.readexcel import Readexcel
from library.ddt import ddt, data
from common.handlepath import data_dir
from common.handleconfig import conf
from common.handlerequests import HandleRequests
from common.handlelog import log
from common.handlemysql import HandleDB
from common.handle_data import CaseData


@ddt
class TeseLoan(unittest.TestCase):
    excel = Readexcel(os.path.join(data_dir, "api_cases_excel.xlsx"), "loan")
    cases = excel.read_data()
    request = HandleRequests()
    basedata = HandleDB()

    @classmethod
    def setUpClass(cls):
        url = conf.get("env", "url") + "/member/login"
        headers = eval(conf.get("env", "headers"))
        data = {
            "mobile_phone": conf.get("test_case", "mobile_phone"),
            "pwd": conf.get("test_case", "pwd")
        }

        response = cls.request.send_requests(url=url, method="post", json=data, headers=headers)
        data = response.json()

        token_type = jsonpath.jsonpath(data, "$..token_type")[0]
        token = jsonpath.jsonpath(data, "$..token")[0]
        CaseData.token_value = token_type + " " + token
        CaseData.member_id = str(jsonpath.jsonpath(data, "$..id")[0])

    @data(*cases)
    def test_loan(self, case):
        # 准备用例数据
        url = conf.get("env", "url") + case["url"]
        headers = eval(conf.get("env", "headers"))
        headers["Authorization"] = getattr(CaseData, "token_value")
        case["data"] = CaseData.replace_data(case["data"])
        data = eval(case["data"])
        expected = eval(case["expected"])
        row = case["case_id"] + 1
        method = case["method"]
        # 发送请求
        # 第一种：通过新增项目数量进行断言
        # if case["check_sql"] ==1:
        #     sql = "select * from futureloan.loan"
        #     start_count = self.basedata.find_count(sql)

        # 第二种：通过新增项目id进行断言
        if case["check_sql"] == 1:
            sql = "select MAX(id) as id from futureloan.loan"
            start_id = self.basedata.find_one(sql)["id"]

        response = self.request.send_requests(method=method, url=url, headers=headers, json=data)
        res = response.json()
        # 断言
        try:
            self.assertEqual(expected["code"], res["code"])
            self.assertEqual(expected["msg"], res["msg"])
            # 通过新增项目数量断言
            # if case["check_sql"] ==1:
            #     sql = "select * from futureloan.loan"
            #     end_count = self.basedata.find_count(sql)
            #     self.assertEqual(end_count-start_count,1)

            # 通过新增项目id进行断言
            if case["check_sql"] == 1:
                sql = "select MAX(id) as id from futureloan.loan where member_id = {}".format(getattr(CaseData, "member_id"))
                end_id = self.basedata.find_one(sql)["id"]
                self.assertEqual(end_id, start_id + 1)

        except AssertionError as e:
            print("预期结果：", expected)
            print("实际结果：", res)
            self.excel.write_data(row=row, column=8, value="不通过")
            log.error("用例：{}执行未通过".format(case["title"]))
            log.exception(e)
            raise e
        else:
            print("预期结果：", expected)
            print("实际结果：", res)
            self.excel.write_data(row=row, column=8, value="通过")
            log.error("用例：{}执行通过".format(case["title"]))
