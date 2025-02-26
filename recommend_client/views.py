import json
from django.http import JsonResponse
from . import user_cf
from . import sentiment_analysis
from . import insertScore
from django.views.decorators.csrf import csrf_exempt


# type CommentRequest struct {
# 	UserID         int    `json:"user_id"`
# 	FoodID         int    `json:"food_id"`
# 	CommentContent string `json:"comment_content"`
# 	Rating         int    `json:"rating"`
# }


@csrf_exempt
def recommend(request):
    if request.method == 'POST':
        try:
            user_cf.run_recommendation_system()
            data = json.loads(request.body)
            user_id = data.get("user_id")
            insertScore.updateScore(user_id)
            return JsonResponse({'statusCode': 200, 'statusContent':"Recommend Finish!"})
        except Exception as e:
            return JsonResponse({'statusCode': 400, 'statusContent': str(e)})

@csrf_exempt
def sent_comment(request):
    if request.method == 'POST':
       try:
           data = json.loads(request.body)
           content = data.get("comment_content")
           user_id = data.get("user_id")
           food_id = data.get("food_id")
           rating = data.get("rating")
           sentiment_analysis.updateScore(user_id, food_id, rating, content)
           return JsonResponse({"statusCode": 200, "statusContent": "Finish!"})
       except Exception as e:
           return JsonResponse({"statusCode": 400, "statusContent":  str(e)})
