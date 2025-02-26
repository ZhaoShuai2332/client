import pymysql

def DB_conn(host="localhost", user="root", password="root", database="food_recommend", port=3306):
    return pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        port=port,
        charset="utf8"
    )

def cal_score(a, b, alpha=0.75):
    return alpha * a + (1 - alpha) * b

def getFinalSentiment(food_id):
    sql = "SELECT sentiment_score FROM comments WHERE food_id = %s"
    conn = DB_conn()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(sql, (food_id,))
            res = cursor.fetchall()
            if not res:
                return 0
            total_score = sum(row['sentiment_score'] for row in res)
            return total_score / len(res)
    finally:
        conn.close()

def cfScore(user_id, food_id):
    sql = "SELECT score FROM recommend_lists WHERE user_id = %s AND food_id = %s"
    conn = DB_conn()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(sql, (user_id, food_id))
            res = cursor.fetchone()
            return res['score'] if res else 0
    finally:
        conn.close()

def getRecommend(user_id):
    sql = "SELECT food_id FROM recommend_lists WHERE user_id = %s"
    conn = DB_conn()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(sql, (user_id,))
            res = cursor.fetchall()
            recommendations = [
                (row['food_id'], cal_score(cfScore(user_id, row['food_id']), getFinalSentiment(row['food_id'])))
                for row in res
            ]
            return recommendations
    finally:
        conn.close()
