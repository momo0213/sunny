'''
***************
Name:Sunny
Time:2020/2/28
***************
'''
import re
from common.handleconfig import conf



class CaseData(object):
    pass

    @staticmethod
    def replace_data(s):
        r = r"#(.+?)#"
        while re.search(r,s):
            res = re.search(r,s)
            # data = res.group()
            key = res.group(1)
            try:
                s = re.sub(r,conf.get("test_case",key),s,1)
            except Exception:
                s = re.sub(r,getattr(CaseData,key),s,1)
        return s


if __name__ == "__main__":
    s = "#mobile_phone#"
    res=CaseData.replace_data(s)
    print(res)

