'''
***************
Name:Sunny
Time:2020/2/25
***************
'''
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# data目录的地址
data_dir = os.path.join(base_dir,"data")

# testcases目录的地址
testcases_dir = os.path.join(base_dir,"testcases")

# conf目录的地址
conf_dir = os.path.join(base_dir,"conf")

# logs目录的地址
logs_dir = os.path.join(base_dir,"logs")

# reports目录的地址
report_dir = os.path.join(base_dir,"reports")