'''
***************
Name:Sunny
Time:2020/3/2
***************
'''
'''
投资接口：
1、需要有标：管理员登录、加标、审核
2、用户登录
3、投资用例的执行

# 关于投资的sql校验
1、用户表：校验用户余额是否发生变化，变化金额等于所投金额（根据用户id去查member表）
2、根据用户id和标id去投资标种查用户的投资记录，（invest里面查用户对应的标是否新增一条记录）
3、根据用户id去流水表种查询流水记录（查询用户投资之后是否多了一条记录）
4、在刚好投满的情况下，可以根据投资记录的id，去回款计划表种查询是否，生成汇款计划

'''
import unittest
import os
import jsonpath
from decimal import Decimal
from library.ddt import ddt, data
from common.readexcel import Readexcel
from common.handlepath import data_dir
from common.handleconfig import conf
from common.handlelog import log
from common.handlerequests import HandleRequests
from common.handle_data import CaseData
from common.handlemysql import HandleDB


@ddt
class TestInvest(unittest.TestCase):
    excel = Readexcel(os.path.join(data_dir, "api_cases_excel.xlsx"), "invest")
    cases = excel.read_data()
    request = HandleRequests()
    bd = HandleDB()

    @data(*cases)
    def test_invest(self, case):
        # 准备用例数据
        url = conf.get("env", "url") + case["url"]
        headers = eval(conf.get("env", "headers"))
        if case["interface"] != "login":
            headers["Authorization"] = getattr(CaseData, "token_value")
        case["data"] = CaseData.replace_data(case["data"])
        data = eval(case["data"])
        method = case["method"]
        expected = eval(case["expected"])
        row = case["case_id"] + 1
        # 校验用户余额是否发生变化，变化前金额（根据用户id去查member表）
        if case["interface"] == "invest" and case["check_sql"] == 1:
            sql_amount = "select * from futureloan.member where mobile_phone = {}".format(
                conf.get("test_case", "admin_mobile_phone"))
            start_money = self.bd.find_one(sql_amount)["leave_amount"]

        # 根据用户id去流水表种查询流水记录（查询用户投资之后是否多了一条记录）
        if case["title"] == "投资成功" and case["check_sql"] == 1:
            sql_invest = "select * from futureloan.financelog where pay_member_id = {}".format(CaseData.member_id)
            start_invest = self.bd.find_one(sql_invest)["pay_member_money"]


        # 发送请求并获取响应结果
        response = self.request.send_requests(url=url, method=method, headers=headers, json=data)
        res = response.json()
        print("预期结果:", expected)
        print("实际结果:", res)

        # 登录后提取token并保存为Casedata类属性
        if case["interface"] == "login":
            token_type = jsonpath.jsonpath(res, "$..token_type")[0]
            token = jsonpath.jsonpath(res, "$..token")[0]
            CaseData.token_value = token_type + " " + token
            CaseData.member_id = str(jsonpath.jsonpath(res, "$..id")[0])
            print(CaseData.member_id)
        # 新增项目后提取项目id并保存为Casedata类属性
        if case["interface"] == "add":
            CaseData.loan_id = str(jsonpath.jsonpath(res, "$..id")[0])

        # 断言
        try:
            self.assertEqual(expected["code"], res["code"])
            self.assertIn(expected["msg"], res["msg"])
            # 校验用户余额是否发生变化，变化后金额（根据用户id去查member表）
            if case["interface"] == "invest" and case["check_sql"] == 1:
                sql_amount = "select * from futureloan.member where mobile_phone = {}".format(
                    conf.get("test_case", "admin_mobile_phone"))
                end_money = self.bd.find_one(sql_amount)["leave_amount"]
                # 取出id作为投资回报表的invest_id
                sql_id = "select * from futureloan.invest where loan_id = {}".format(CaseData.loan_id)
                CaseData.invest_id = self.bd.find_one(sql_id)["id"]
                # 校验invest投资标新增一条投资记录
                sql_loan_id = "select * from futureloan.invest where loan_id = {}".format(CaseData.loan_id)
                count_loan_id = self.bd.find_one(sql_loan_id)["loan_id"]
                self.assertEqual(start_money - end_money, Decimal(str(data["amount"])))
                self.assertEqual(count_loan_id, int(getattr(CaseData, "loan_id")))

            # 根据用户id去流水表种查询流水记录（查询用户投资之后是否多了一条记录）
            if case["title"] == "投资成功" and case["check_sql"] == 1:
                sql_invest = "select * from futureloan.financelog where pay_member_id = {}".format(CaseData.member_id)
                end_invest = self.bd.find_one(sql_invest)["pay_member_money"]
                self.assertEqual(start_invest - end_invest, Decimal(str(data["amount"])))

            # 在刚好投满的情况下，根据投资记录的id，去回款计划表种查询生成的汇款计划
            if case["title"] == "用户投资金额等于项目标金额" and case["check_sql"] == 1:
                sql_invest_id = "select * from futureloan.repayment where invest_id = {}".format(
                getattr(CaseData, "invest_id"))
                repay_count = self.bd.find_count(sql_invest_id)
                self.assertTrue(repay_count)

        except AssertionError as e:
            self.excel.write_data(row=row, column=8, value="不通过")
            log.error("用例：{} 执行不通过".format(case["title"]))
            log.exception(e)
            raise e
        else:
            self.excel.write_data(row=row, column=8, value="通过")
            log.info("用例：{} 执行通过".format(case["title"]))
