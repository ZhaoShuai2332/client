import pymysql
from . import user_cf

DBoperator = user_cf.DBOperator()

def cal_score(a, b, alpha=0.75):
    return alpha * a + (1 - alpha) * b


