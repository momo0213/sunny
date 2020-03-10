'''
***************
Name:Sunny
Time:2020/2/25
***************
'''
import openpyxl
class Readexcel(object):
    def __init__(self,file_name,sheet_name):
        self.file_name = file_name
        self.sheet_name = sheet_name

    def open(self):
        # 创建一个工作簿对象
        self.workbook = openpyxl.load_workbook(self.file_name)
        # 读取工作簿中的表单
        self.sheet = self.workbook[self.sheet_name]

    def read_data(self):
        self.open()
        # 读取出表单中每一行的数据
        case_datas = list(self.sheet.rows)
        # 把第一行数据取出作为字典的键
        title = [title.value for title in case_datas[0]]
        # 把除第一行以外的数据取出作为字典的值
        li = []
        for case_data in case_datas[1:]:
            values = [data.value for data in case_data]
            # 将数据打包成字典
            cases = dict(zip(title,values))
            li.append(cases)

        return li

    def write_data(self,row,column,value):
        self.open()
        # 往表单中写入数据
        self.sheet.cell(row=row,column=column,value=value)
        # 保存工作簿
        self.workbook.save(self.file_name)

