from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import House, FinishingOption, HouseCategory, PurchasedHouse, Review


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



