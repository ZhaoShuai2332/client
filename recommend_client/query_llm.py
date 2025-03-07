import pymysql

def insert_recommendations(email, sql_query):
    connection = pymysql.connect(
        host="127.0.0.1",
        user="root",
        password="root",
        database="food_recommend",
        cursorclass=pymysql.cursors.DictCursor
    )
    
    try:
        with connection.cursor() as cursor:
            # 1. 获取 user_id
            cursor.execute("SELECT user_id FROM users WHERE user_email = %s", (email,))
            print(email)
            user = cursor.fetchone()
            if not user:
                print("User not found!")
                return
            user_id = user["user_id"]

            # 2. 查询推荐食物
            cursor.execute(sql_query)
            foods = cursor.fetchall()
            if not foods:
                # print("No food recommendations found!")
                return

            # 3. 插入推荐记录
            insert_query = "INSERT INTO recommend_lists (user_id, food_id, score) VALUES (%s, %s, %s)"
            values = [(user_id, food["food_id"], 3) for food in foods]
            cursor.executemany(insert_query, values)

            # 提交事务
            connection.commit()
            # print("Recommendations inserted successfully!")
    
    finally:
        connection.close()