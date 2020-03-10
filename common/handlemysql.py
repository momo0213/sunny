'''
***************
Name:Sunny
Time:2020/2/26
***************
'''
'''
数据库地址：120.78.128.25
port：3306
用户：future
密码：123456
'''
import pymysql
from common.handleconfig import conf


class HandleDB(object):
    def __init__(self):
        # 连接数据库
        self.connect = pymysql.connect(host=conf.get("bd", "host"),
                                       port=conf.getint("bd", "post"),
                                       user=conf.get("bd", "user"),
                                       password=conf.get("bd", "password"),
                                       charset=conf.get("bd", "charset"),
                                       cursorclass=pymysql.cursors.DictCursor)

        # 创建一个游标对象
        self.cur = self.connect.cursor()

    def find_one(self, sql):
        # 提交事务，查询一条数据
        self.connect.commit()
        self.cur.execute(sql)
        data = self.cur.fetchone()
        return data

    def find_all(self, sql):
        # 提交事务，查询所有数据
        self.connect.commit()
        self.cur.execute(sql)
        data = self.cur.fetchall()
        return data

    def find_count(self, sql):
        self.connect.commit()
        count = self.cur.execute(sql)
        return count


    def close(self):
        # 关闭游标，关闭连接
        self.cur.close()
        self.connect.close()

if __name__ == "__main__":
    bd = HandleDB()
    sql_id = "select * from futureloan.invest where loan_id = 30424"
    invest_id = bd.find_one(sql_id)["id"]
    print(invest_id)
