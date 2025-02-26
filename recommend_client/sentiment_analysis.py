from transformers import BertTokenizer, BertForSequenceClassification
import torch
import pymysql

def DB_conn(host="localhost", user="root", password="root", database="food_recommend", port=3306):
    return pymysql.connect(
                    host = host,
                    user = user,
                    password = password,
                    database = database,
                    port = port,
                    charset = "utf8"
                )

def bert_sentiment_analysis(text):
    # D:\projects\admin_sys\client\recommend_client\bert_model\sentiment_model
    bert_path = 'recommend_client/bert_model/sentiment_model'

    tokenizer = BertTokenizer.from_pretrained(bert_path)
    bert_model = BertForSequenceClassification.from_pretrained(bert_path, num_labels=5, ignore_mismatched_sizes=True)

    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    outputs = bert_model(**inputs)

    probabilities = torch.nn.functional.softmax(outputs.logits, dim=1)
    predicted_score = torch.argmax(probabilities, dim=1).item()

    return predicted_score + 1

def updateScore(user_id, food_id, ratings, content):
    conn = DB_conn()
    cursor =  conn.cursor()
    sentiment_score = bert_sentiment_analysis(content)
    sql = "UPDATE comments SET sentiment_score = %s WHERE user_id = %s AND food_id = %s AND rating = %s AND comment = %s"
    try:
        cursor.execute(sql, (sentiment_score, user_id, food_id, ratings, content))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()
