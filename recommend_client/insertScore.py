import pymysql
from . import getScore

def DB_conn(host="localhost", user="root", password="root", database="food_recommend", port=3306):
    return pymysql.connect(
                    host = host,
                    user = user,
                    password = password,
                    database = database,
                    port = port,
                    charset = "utf8"
                )

def updateScore(user_id):
    recommendation = getScore.getRecommend(user_id)
    sql = "UPDATE recommend_lists SET score = %s WHERE user_id = %s and food_id = %s"
    conn = DB_conn()
    cursor = conn.cursor()
    try:
        for item in recommendation:
            cursor.execute(sql, (item['score'], user_id, item['food_id']))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

