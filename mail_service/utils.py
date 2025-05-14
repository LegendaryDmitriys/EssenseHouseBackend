# notifications/utils.py
import json
from webpush import send_webpush, WebPushException
from django.conf import settings
from .models import PushSubscription


def send_push_notification(subscription_data, title='Уведомление', body='Новое сообщение'):
    try:
        payload = json.dumps({
            "title": title,
            "body": body,
            "icon": "/static/icons/icon-192.png",  # путь к иконке
            "badge": "/static/icons/badge-72.png",
            "data": {
                "url": "/"  # например, куда перейти по клику
            }
        })

        send_webpush(
            subscription_info=subscription_data,
            data=payload,
            vapid_private_key=settings.VAPID_PRIVATE_KEY,
            vapid_claims={
                "sub": settings.VAPID_CLAIM_EMAIL
            }
        )
    except WebPushException as ex:
        print(f"Ошибка при отправке уведомления: {repr(ex)}")