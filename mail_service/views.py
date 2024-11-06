from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from backend.models import UserQuestionHouse
from .utils import send_email
from .utils import fetch_emails

from django.core.mail import send_mail
from django.http import JsonResponse


class SendEmailView(APIView):
    def post(self, request):
        subject = request.data.get('subject')
        message = request.data.get('message')
        recipient_list = request.data.get('recipient_list')

        if not subject or not message or not recipient_list:
            return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

        send_email(subject, message, recipient_list)
        return Response({'success': 'Email sent successfully'}, status=status.HTTP_200_OK)


class FetchEmailsView(APIView):
    def get(self, request):
        print("Get method called")
        category = request.query_params.get('category', 'inbox')
        print(f"Requested category: {category}")
        emails = fetch_emails(category)
        return Response(emails)

import json

@csrf_exempt
def send_answer(request):
    if request.method == "POST":
        try:

            data = json.loads(request.body)
            email = data.get("email")
            question_id = data.get("questionId")
            answer = data.get("answer")

            question = UserQuestionHouse.objects.get(id=question_id)

            subject = f"Ответ на ваш вопрос по поводу дома"
            message = f"Ваш вопрос: {question.question}\nОтвет: {answer}"
            from_email = "EssenseHouse"

            send_mail(subject, message, from_email, [email])

            question.status = 'answered'
            question.save()

            return JsonResponse({"message": "Ответ отправлен на почту."}, status=200)

        except UserQuestionHouse.DoesNotExist:
            return JsonResponse({"message": "Не удалось отправить ответ.", "error": "Вопрос не найден."}, status=404)
        except Exception as e:
            return JsonResponse({"message": "Не удалось отправить ответ.", "error": str(e)}, status=500)