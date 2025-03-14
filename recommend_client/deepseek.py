from openai import OpenAI
import re, json

client = OpenAI(
    base_url='http://localhost:11434/v1/',
    api_key='ollama',
)

def generate_prompt(email, food_preferences, taste_preferences, diet_goals):
    prompt = f"""
    I need to generate a cold-start recommendation for a new user to provide personalized food suggestions upon registration.
    
    #### **User Information**  
    - **Email**: {email}  
    - **Taste Preference**: {taste_preferences}  
    - **Food Preference**: {food_preferences}  
    - **Diet Goal**: {diet_goals}  

    #### **Database Information**  
    - **Table Name**: `foods`  
    - **Fields**:  
      - `id` (Primary Key)  
      - `name` (Food Name)  
      - `food_description` (Food Description, including taste, ingredients, cuisine, etc.)  

    #### **Keyword Generation Requirements**  
    1. Generate **50 keywords** to match relevant foods in the `description` field of the `foods` table.  
    2. Keywords should align with user preferences ({taste_preferences}, {food_preferences}, {diet_goals}) and cover various descriptive expressions.  
    3. Keywords must be strictly relevant to what may appear in the `description` field to avoid generating unrelated words.  

    #### **SQL Query Generation Requirements**  
    1. Based on the recommended keywords, generate an **SQL query** to filter foods that match user preferences.  
    2. Select **only 5 foods** for recommendation (`LIMIT 5`).  
    3. **Query Method**: The `description` field should use `LIKE` for fuzzy matching, combined with the `OR` logic.  

    #### **Final Output Format (JSON)**  
    Please strictly return the result in the following JSON format:  

    ```json
    {{
      "keywords": [
        "spicy", "Sichuan cuisine", "hot and numbing", "red oil", "chili pepper", 
        "... (50 keywords in total)"
      ],
      "sql_query": "SELECT * FROM foods WHERE food_description LIKE '%spicy%' OR food_description LIKE '%Sichuan cuisine%' OR food_description LIKE '%muscle gain%' OR food_description LIKE '%high protein%' OR food_description LIKE '%hot and numbing%' LIMIT 5;"
    }}
    ```

    Ensure that the `keywords` array contains exactly 50 recommended keywords and that `sql_query` follows correct SQL syntax for direct database executio, Please provide the answer directly without explaining the thought process.
    """
    return prompt


def chat_with_ai(prompt, user = 'user'):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                'role': user,
                'content': prompt,
            }
        ],
        model='deepseek-r1:8b',
    )
    return chat_completion.choices[0].message.content

def extract_sql_from_response(response):
    """
    从 LLM 响应中提取 SQL 语句，仅使用 re 解析。
    """
    sql_pattern = r'"sql_query"\s*:\s*"((SELECT .*?;))"'

    match = re.search(sql_pattern, response, re.DOTALL | re.IGNORECASE)
    
    if match:
        sql_query = match.group(1).strip()
        return sql_query
    else:
        sql_pattern_alt = r"SELECT .*?;"
        match_alt = re.search(sql_pattern_alt, response, re.DOTALL | re.IGNORECASE)
        
        if match_alt:
            return match_alt.group(0).strip()
        
    return None  

def extract_keywords_from_prompt(response):
    """
    使用正则表达式从 prompt 字符串中提取 'keywords' 数组
    """
    keywords_pattern = r'"keywords":\s*\[(.*?)\]'
    match = re.search(keywords_pattern, response, re.DOTALL)

    if not match:
        return None  

    keywords_str = match.group(1)

    keywords_str = "[" + keywords_str.strip() + "]"
    keywords_str = keywords_str.replace("...", "").replace("(50 keywords in total)", "").strip()

    try:
        keywords_list = json.loads(keywords_str)
        return keywords_list
    except json.JSONDecodeError:
        return None  