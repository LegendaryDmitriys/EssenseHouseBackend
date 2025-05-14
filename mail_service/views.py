import json

from django.views.decorators.csrf import csrf_exempt
from .models import PushSubscription

from backend.models import UserQuestionHouse


from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse
from django.conf import settings
from pywebpush import webpush, WebPushException
import json



@csrf_exempt
def send_answer(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get("email")
            question_id = data.get("questionId")
            answer = data.get("answer")

            if not all([email, question_id, answer]):
                return JsonResponse({
                    "message": "Некорректные данные",
                    "error": "email, questionId и answer обязательны"
                }, status=400)

            question = UserQuestionHouse.objects.get(id=question_id)

            subject = "Ваш вопрос по дому — ответ от Essense House"
            from_email = "noreply@essensehouse.ru"
            to_email = [email]

            text_content = (
                f"Здравствуйте, {question.name}!\n\n"
                f"Вы спрашивали:\n{question.question}\n\n"
                f"Ответ от нашей команды:\n{answer}\n\n"
                f"С уважением,\nКоманда Essense House"
            )

            html_content = f"""
                            <html>
                            <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px;">
                                <div style="max-width: 600px; margin: 0 auto; background: #fff; border-radius: 10px; padding: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                                    <div style="text-align: center; margin-bottom: 20px;">
                                        <img src="http://192.168.0.103:8000/media/mail/logo.png" alt="Essense House" style="height: 60px;" />
                                    </div>
                                    <h2 style="color: #2d3748;">Здравствуйте, {question.name}!</h2>
                                    <p style="color: #4a5568; font-size: 15px;">Вы спрашивали:</p>
                                    <div style="background: #f1f5f9; padding: 15px; border-radius: 6px; margin-bottom: 20px;">
                                        <p style="margin: 0; color: #1a202c;">{question.question}</p>
                                    </div>
                                    <p style="color: #4a5568; font-size: 15px;">Наш ответ:</p>
                                    <div style="background: #e6fffa; padding: 15px; border-radius: 6px;">
                                        <p style="margin: 0; color: #1a202c;">{answer}</p>
                                    </div>
                                    <hr style="margin: 30px 0; border: none; border-top: 1px solid #e2e8f0;" />
                                    <p style="font-size: 13px; color: #718096;">С уважением,<br>Команда <a href="https://essensehouse.ru" style="color: #3182ce; text-decoration: none;">Essense House</a></p>
                                </div>
                            </body>
                            </html>
                        """

            msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            question.status = 'answered'
            question.save()

            return JsonResponse({"message": "Ответ отправлен на почту."}, status=200)

        except UserQuestionHouse.DoesNotExist:
            return JsonResponse({
                "message": "Вопрос не найден.",
                "error": "Неверный questionId"
            }, status=404)

        except Exception as e:
            return JsonResponse({
                "message": "Произошла ошибка при отправке письма.",
                "error": str(e)
            }, status=500)




@csrf_exempt
def save_subscription(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        PushSubscription.objects.create(
            endpoint=data['endpoint'],
            keys=data['keys']
        )
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'Неверный метод'}, status=400)


@csrf_exempt
def send_notification_to_all(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            title = data.get('title', 'Новое уведомление')
            body = data.get('body', 'Проверка push-уведомлений!')
            icon = data.get('icon', '/media/push/icon.png')
            badge = data.get('badge', '/media/push/badge.png')

            subscriptions = PushSubscription.objects.all()
            for sub in subscriptions:
                webpush(
                    subscription_info={
                        "endpoint": sub.endpoint,
                        "keys": sub.keys
                    },
                    data=json.dumps({"title": title, "body": body, "icon": icon, "badge": badge}),
                    vapid_private_key=settings.VAPID_PRIVATE_KEY,
                    vapid_claims=settings.VAPID_CLAIMS
                )
            return JsonResponse({'status': 'Уведомления отправлены!'})
        except WebPushException as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Только POST-запросы!'}, status=405)