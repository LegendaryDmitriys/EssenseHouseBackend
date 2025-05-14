from django.urls import path
from .views import send_answer, save_subscription, send_notification_to_all

urlpatterns = [
    path("send-answer/", send_answer, name="Отправка письма"),
    path('subscribe', save_subscription, name="Подписка на Push-уведомления"),
    path('send-notification/', send_notification_to_all, name='Отправка Push-уведомлений'),
]