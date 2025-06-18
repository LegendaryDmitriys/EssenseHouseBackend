from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.core.cache import cache

from auth_app.models import User
from mail_service.views import send_notification_to_user
from .models import House, FinishingOption, HouseCategory, PurchasedHouse, Review, Order, UserQuestionHouse


@receiver(post_save, sender=House)
@receiver(post_delete, sender=House)
def clear_house_cache(sender, instance, **kwargs):
    cache_key = f"house_detail_{instance.id}"
    cache.delete(cache_key)

@receiver(post_save, sender=FinishingOption)
@receiver(post_delete, sender=FinishingOption)
def clear_finishing_option_cache(sender, instance, **kwargs):
    cache.delete("finishing_options_list")
    cache.delete(f"finishing_option_{instance.id}")

@receiver(post_save, sender=HouseCategory)
@receiver(post_delete, sender=HouseCategory)
def clear_house_category_cache(sender, instance, **kwargs):
    cache.delete(f"house_category_{instance.slug}")
    cache.delete("house_category_list")

@receiver(post_save, sender=PurchasedHouse)
@receiver(post_delete, sender=PurchasedHouse)
def clear_purchase_house_cache(sender, instance, **kwargs):
    cache.delete(f"purchase_house_{instance.pk}")
    cache.delete("purchase_house_list")

@receiver(post_save, sender=Review)
@receiver(post_delete, sender=Review)
def clear_reviews_cache(sender, instance, **kwargs):
    cache.delete(f"review_{instance.pk}")
    cache.delete("reviews_list")


_order_old_status = {}
_question_old_status = {}
_purchase_old_status = {}
_review_old_status = {}

@receiver(pre_save, sender=Order)
def cache_old_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            _order_old_status[instance.pk] = sender.objects.get(pk=instance.pk).status
        except sender.DoesNotExist:
            _order_old_status[instance.pk] = None

@receiver(post_save, sender=Order)
def notify_user_on_status_change(sender, instance, created, **kwargs):
    if created:
        return

    old_status = _order_old_status.pop(instance.pk, None)
    new_status = instance.status

    if old_status != new_status:
        user = User.objects.filter(email=instance.email).first()
        if user:
            send_notification_to_user(
                user=user,
                title="Обновление статуса вашего заказа",
                body=f"Статус вашего заказа на дом «{instance.house.title}» изменился: теперь он — {instance.get_status_display()}. Подробности в вашем профиле!",
                link="/profile/orders"
            )
        else:
            print("Пользователь с таким email не найден")
    else:
        print("Статус не изменился — пуш не нужен")


@receiver(pre_save, sender=UserQuestionHouse)
def cache_old_question_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            _question_old_status[instance.pk] = sender.objects.get(pk=instance.pk).status
        except sender.DoesNotExist:
            _question_old_status[instance.pk] = None

@receiver(post_save, sender=UserQuestionHouse)
def notify_user_on_question_status_change(sender, instance, created, **kwargs):
    if created:
        return
    old_status = _question_old_status.pop(instance.pk, None)
    if old_status != instance.status:
        if instance.email:
            user = User.objects.filter(email=instance.email).first()
            if user:
                send_notification_to_user(
                    user=user,
                    title="Ответ на ваш вопрос",
                    body=f"Мы обновили статус вашего вопроса по дому «{instance.house.title}» — теперь он: {instance.get_status_display()}. Подробности ждут вас в профиле!",
                    link="/profile"
                )

@receiver(pre_save, sender=PurchasedHouse)
def cache_old_construction_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            _purchase_old_status[instance.pk] = sender.objects.get(pk=instance.pk).construction_status
        except sender.DoesNotExist:
            _purchase_old_status[instance.pk] = None

@receiver(post_save, sender=PurchasedHouse)
def notify_user_on_construction_status_change(sender, instance, created, **kwargs):
    if created:
        return
    old_status = _purchase_old_status.pop(instance.pk, None)
    if old_status != instance.construction_status:
        user = User.objects.filter(email=instance.email).first()
        if user:
            send_notification_to_user(
                user=user,
                title="Обновление статуса строительства дома",
                body=f"Статус строительства дома «{instance.house.title}» изменился — теперь он: {instance.get_construction_status_display()}. Следите за прогрессом в вашем профиле!",
                link="/profile"
            )

@receiver(pre_save, sender=Review)
def cache_old_review_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            _review_old_status[instance.pk] = sender.objects.get(pk=instance.pk).status
        except sender.DoesNotExist:
            _review_old_status[instance.pk] = None

@receiver(post_save, sender=Review)
def notify_user_on_review_status_change(sender, instance, created, **kwargs):
    if created:
        return
    old_status = _review_old_status.pop(instance.pk, None)
    if old_status != instance.status and instance.status == 'published':
        print("old_status:", old_status)
        print("new_status:", instance.status)
        print("email:", instance.email)
        if instance.email:
            user = User.objects.filter(email=instance.email).first()
            if user:
                print("user:", user)
                send_notification_to_user(
                    user=user,
                    title="Ваш отзыв опубликован!",
                    body="Спасибо за ваш отзыв! Он теперь доступен на сайте для всех пользователей.",
                    link="/comments"
                )

