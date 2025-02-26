import math
from operator import itemgetter
import pymysql

class DBOperator:
    def __init__(self, host="localhost", user="root", password="root", database="food_recommend", port=3306):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.conn = None

    def connect(self):
        """ 连接数据库 """
        if self.conn is None:
            try:
                self.conn = pymysql.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    port=self.port,
                    charset="utf8"
                )
            except Exception as e:
                print("Database connection failed!", e)
                self.conn = None

    def close(self):
        """ 关闭数据库连接 """
        if self.conn:
            self.conn.close()
            self.conn = None

    def execute_query(self, query, params=None):
        """ 执行查询语句，返回结果 """
        self.connect()
        if self.conn is None:
            return None
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, params or ())
                return cursor.fetchall()
        except Exception as e:
            print("Query execution failed!", e)
            return None

    def execute_update(self, query, params=None):
        """ 执行增删改语句 """
        self.connect()
        if self.conn is None:
            return False
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, params or ())
                self.conn.commit()
            return True
        except Exception as e:
            print("Update execution failed!", e)
            return False


class UserBasedCF:
    def __init__(self, n_sim_user=3, n_rec_food=5):
        self.n_sim_user = n_sim_user  # 选择最相似的用户数
        self.n_rec_food = n_rec_food  # 每个用户推荐的美食数
        self.trainSet = {}  # 训练数据
        self.user_sim_matrix = {}  # 用户相似度矩阵
        self.food_count = 0  # 美食总数
        self.db = DBOperator()  # 使用 DBOperator 进行数据库操作

    def load_data_from_db(self):
        """ 直接从数据库读取用户-美食数据 """
        query = "SELECT user_id, food_id FROM wish_lists"
        data = self.db.execute_query(query)

        if data:
            for user, food in data:
                self.trainSet.setdefault(user, {})
                self.trainSet[user][food] = 1  # 评分默认为1（表示交互）

    def calc_user_sim(self):
        """ 计算用户相似度 """
        food_user = {}
        for user, foods in self.trainSet.items():
            for food in foods:
                food_user.setdefault(food, set()).add(user)

        self.food_count = len(food_user)

        for food, users in food_user.items():
            for u in users:
                for v in users:
                    if u == v:
                        continue
                    self.user_sim_matrix.setdefault(u, {}).setdefault(v, 0)
                    self.user_sim_matrix[u][v] += 1

        # 计算相似性
        for u, related_users in self.user_sim_matrix.items():
            for v, count in related_users.items():
                self.user_sim_matrix[u][v] = count / math.sqrt(len(self.trainSet[u]) * len(self.trainSet[v]))

    def recommend(self, user):
        """ 为用户生成美食推荐 """
        K, N = self.n_sim_user, self.n_rec_food
        rank = {}
        watched_foods = self.trainSet.get(user, {})

        for v, wuv in sorted(self.user_sim_matrix.get(user, {}).items(), key=itemgetter(1), reverse=True)[:K]:
            for food in self.trainSet[v]:
                if food in watched_foods:
                    continue
                rank.setdefault(food, 0)
                rank[food] += wuv
        return sorted(rank.items(), key=itemgetter(1), reverse=True)[:N]

    def save_recommendations_to_db(self):
        """ 计算推荐并存入数据库 """
        self.db.execute_update("TRUNCATE TABLE recommend_lists;")  # 清空原有数据
        query = "INSERT INTO recommend_lists(user_id, food_id, score) VALUES (%s, %s, %s)"

        recommendations = []
        for user in self.trainSet:
            rec_foods = self.recommend(user)
            for food, score in rec_foods:
                recommendations.append((user, food, score))

        # 批量插入数据
        if recommendations:
            self.db.execute_update(query, recommendations)

def run_recommendation_system():
    userCF = UserBasedCF()
    userCF.load_data_from_db()
    userCF.calc_user_sim()
    userCF.save_recommendations_to_db()

# if __name__ == '__main__':
#     run_recommendation_system()
