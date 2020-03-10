'''
***************
Name:Sunny
Time:2020/2/25
***************
'''
import unittest
import os
import datetime
from library.HTMLTestRunnerNew import HTMLTestRunner
from common.handlepath import testcases_dir,report_dir
from common.handle_email import SendEmail
from testcases import recharge,testcase,test_loan,withdraw,register,audit,invest,test_main_stream
from BeautifulReport import BeautifulReport

date = datetime.datetime.now().strftime("%Y-%m-%d")
# 创建测试套件
suite = unittest.TestSuite()
# 将测试用例加载到测试套件中
loader = unittest.TestLoader()
suite.addTest(loader.loadTestsFromModule(test_main_stream))
# 执行测试用例
runner = HTMLTestRunner(stream=open(os.path.join(report_dir,date+"report.html"),"wb"),
                        title="测试报告0225",
                        description="接口实战练习",
                        tester="Sunny")
runner.run(suite)

# br = BeautifulReport(suite)
# br.report("前程带项目用例",filename=date+"report.html",report_dir=report_dir)


# SendEmail.send_email("report.html","在测试套件中执行一遍发邮件")
