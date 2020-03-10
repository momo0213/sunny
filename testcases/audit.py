'''
***************
Name:Sunny
Time:2020/3/2
***************
'''
'''
关于审核的步骤分析：
1、要登录（所有的审核用例执行之前，登录就可以了）
2、添加项目（每一个用例执行之前都要加标）
3、审核


'''
import unittest
import os
import jsonpath
from library.ddt import ddt, data
from common.readexcel import Readexcel
from common.handlepath import data_dir
from common.handleconfig import conf
from common.handlerequests import HandleRequests
from common.handlelog import log
from common.handle_data import CaseData
from common.handlemysql import HandleDB

@ddt
class TestAudit(unittest.TestCase):
    excel = Readexcel(os.path.join(data_dir, "api_cases_excel.xlsx"), "audit")
    cases = excel.read_data()
    request = HandleRequests()
    db = HandleDB()


    @classmethod
    def setUpClass(cls):
        # 登录系统
        url = conf.get("env", "url") + "/member/login"
        headers = eval(conf.get("env", "headers"))
        data = {
            "mobile_phone": conf.get("test_case", "admin_mobile_phone"),
            "pwd": conf.get("test_case", "admin_pwd")
        }
        response = cls.request.send_requests(url=url, method="post", json=data, headers=headers)
        data = response.json()
        token_type = jsonpath.jsonpath(data, "$..token_type")[0]
        token = jsonpath.jsonpath(data, "$..token")[0]
        CaseData.token_value = token_type + " " + token
        CaseData.member_id = jsonpath.jsonpath(data, "$..id")[0]

    def setUp(self):
        '''进行加标'''
        # 1、准备加标的数据
        url = conf.get("env", "url") + "/loan/add"
        headers = eval(conf.get("env", "headers"))
        headers["Authorization"] = getattr(CaseData, "token_value")
        data = {
            "member_id": getattr(CaseData, "member_id"),
            "title": "报名 python 全栈自动化课程",
            "amount": 300,
            "loan_rate": 12.0,
            "loan_term": 30,
            "loan_date_type": 2,
            "bidding_days": 10
        }
        # 2、发送请求，添加项目
        response = self.request.send_requests(url=url, method="post", json=data, headers=headers)
        data = response.json()
        # 3、提取审核需要用到的项目id
        CaseData.loan_id = str(jsonpath.jsonpath(data, "$..id")[0])

    @data(*cases)
    def test_audit(self, case):
        # 准备数据
        url = conf.get("env", "url") + case["url"]
        headers = eval(conf.get("env", "headers"))
        headers["Authorization"] = getattr(CaseData, "token_value")
        case["data"] = CaseData.replace_data(case["data"])
        data = eval(case["data"])
        expexted = eval(case["expected"])
        method = case["method"]
        row = case["case_id"] + 1
        # 发送请求并获取相应结果
        response = self.request.send_requests(url=url, method=method, headers=headers, json=data)
        res = response.json()
        # 获取第一条审核通过的loan_id
        if case["title"] == "新增项目审核成功" and res["code"] == 0:
            CaseData.pass_loan_id = str(jsonpath.jsonpath(res,"$..id"))
        print("预期结果：", expexted)
        print("实际结果：", res)
        # 断言
        try:
            self.assertEqual(expexted["code"], res["code"])
            self.assertEqual(expexted["msg"], res["msg"])
            # 数据库校验
            if expexted["code"] == 0:
                sql = "select status from futureloan.loan where id = {}".format(CaseData.loan_id)
                status = self.db.find_one(sql)["status"]
                self.assertEqual(expexted["status"],status)
        except AssertionError as e:
            self.excel.write_data(row=row, column=8, value="不通过")
            log.error("用例：{} 执行不通过".format(case["title"]))
            log.exception(e)
            raise e
        else:
            self.excel.write_data(row=row, column=8, value="通过")
            log.info("用例：{} 执行通过".format(case["title"]))
