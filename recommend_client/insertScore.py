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
    recommendation = getScore.getRecommend(user_id)  # Removed getScore. since it's a function
    sql = "UPDATE recommend_lists SET score = %s WHERE user_id = %s and food_id = %s"
    conn = DB_conn()
    cursor = conn.cursor()
    try:
        for item in recommendation:
            # print(item)
            cursor.execute(sql, (item[1], user_id, item[0]))  # Use tuple indices instead of dictionary keys
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()
