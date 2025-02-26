from django.http import JsonResponse
from . import user_cf
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def recommend(request):
    if request.method == 'POST':
        try:
            user_cf.run_recommendation_system()
            return JsonResponse({'statusCode': 200, 'statusContent':"Recommend Finish!"})
        except Exception as e:
            return JsonResponse({'statusCode': 400, 'statusContent': str(e)})

@csrf_exempt
def sent_comment(request):
    if request.method == 'POST':
        try:
