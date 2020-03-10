'''
***************
Name:Sunny
Time:2020/3/2
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
        sql = "select mobile_phone from futureloan.member"
        phone = "133"
        for i in range(8):
            num = random.randint(1, 9)
            phone += str(num)
            base_phone = self.basedata.find_all(sql)
            if phone == base_phone:
                phone += str(num)
        return phone