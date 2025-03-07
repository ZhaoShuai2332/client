import pymysql
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def insert_recommendations(email, sql_query, keywords):
    connection = pymysql.connect(
        host="127.0.0.1",
        user="root",
        password="root",
        database="food_recommend",
        cursorclass=pymysql.cursors.DictCursor
    )
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT user_id FROM users WHERE user_email = %s", (email,))
            print(email)
            user = cursor.fetchone()
            if not user:
                print("User not found!")
                return
            user_id = user["user_id"]

            cursor.execute(sql_query)
            foods = cursor.fetchall()
            if not foods:
                return

            insert_query = "INSERT INTO recommend_lists (user_id, food_id, score) VALUES (%s, %s, %s)"
            values = [(user_id, food["food_id"], calculate_tfidf_similarity(keywords, food["food_description"])) for food in foods]
            cursor.executemany(insert_query, values)

            connection.commit()
    
    finally:
        connection.close()

def calculate_tfidf_similarity(user_keywords, food_description):
    """
    使用 TF-IDF 计算用户偏好与食物描述的相似度
    :param user_keywords: list 用户选择的偏好文本
    :param food_description: str 食物描述（单个）
    :return: float 相似度得分(0~1)
    """
    vectorizer = TfidfVectorizer()
    
    documents = [" ".join(user_keywords), food_description]

    tfidf_matrix = vectorizer.fit_transform(documents)

    similarity_score = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0]
    return round(1 + (similarity_score * 4), 2)  # 1~5
