import os

from django.db import models
from django.utils.text import slugify
import random
from django.db.models import Count
from django.utils import timezone

class HouseCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    short_description = models.TextField(null=True, blank=True)
    long_description = models.TextField(null=True, blank=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_random_image(self):
        houses_with_images = self.houses.annotate(num_images=Count('images')).filter(num_images__gt=0)
        if houses_with_images.exists():
            random_house = random.choice(houses_with_images)
            return random.choice(random_house.images.all()).image.url
        return None



class ConstructionTechnology(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class House(models.Model):
    BESTSELLER_CHOICES = [
        ('Акция', 'Акция'),
        ('Новинка', 'Новинка'),
    ]

    PURPOSE_CHOICES = [
        ('Частный дом', 'Частный дом'),
        ('Коммерческая недвижимость', 'Коммерческая недвижимость'),
    ]

    title = models.CharField(max_length=100, unique=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                    verbose_name="Старая цена")
    discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                   verbose_name="Скидка")
    new = models.BooleanField(default=True, verbose_name="Новый продукт")
    best_seller = models.CharField(max_length=10, choices=BESTSELLER_CHOICES, blank=True, null=True)
    area = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Площадь, м²")
    floors = models.PositiveIntegerField()
    rooms = models.PositiveIntegerField()
    living_area = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Жилая площадь, м²")
    kitchen_area = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    bedrooms = models.PositiveIntegerField()
    bathrooms = models.PositiveIntegerField(verbose_name="Количество санузлов", null=True, blank=True)
    garage = models.BooleanField(default=False)
    garage_capacity = models.PositiveIntegerField(verbose_name="Гараж (кол-во машин)", null=True, blank=True)
    purpose = models.CharField(max_length=30, choices=PURPOSE_CHOICES)
    warranty = models.PositiveIntegerField(verbose_name="Гарантия, лет", null=True, blank=True)
    construction_time = models.PositiveIntegerField(verbose_name="Срок строительства, дней", null=True, blank=True)
    construction_technology = models.ForeignKey(ConstructionTechnology, on_delete=models.CASCADE)
    category = models.ForeignKey(HouseCategory, on_delete=models.CASCADE, related_name='houses')
    description = models.TextField(verbose_name="Описание", null=True, blank=True)


    def __str__(self):
        return f"Дом {self.pk} - {self.price} руб."


class HouseImage(models.Model):
    house = models.ForeignKey(House, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='houses/')

    def __str__(self):
        return f"Изображение для дома {self.house.pk}"

class HouseInteriorImage(models.Model):
    house = models.ForeignKey(House, related_name='interior_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='houses/interior/')

    def __str__(self):
        return f"Изображение интерьера для дома {self.house.pk}"

class HouseFacadeImage(models.Model):
    house = models.ForeignKey(House, related_name='facade_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='houses/facades/')

    def __str__(self):
        return f"Изображение фасада для дома {self.house.pk}"

class HouseLayoutImage(models.Model):
    house = models.ForeignKey(House, related_name='layout_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='houses/layouts/')

    def __str__(self):
        return f"Изображение планировки для дома {self.house.pk}"


class FinishingOption(models.Model):
    house = models.ForeignKey('House', on_delete=models.CASCADE, related_name='finishing_options')
    title = models.CharField(max_length=100, verbose_name='Заголовок')
    description = models.TextField(verbose_name="Описание")
    price_per_sqm = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена за м²", null=True, blank=True)
    image = models.ImageField(upload_to='houses/finishing_options/', verbose_name='Изображение', null=True, blank=True)

    def __str__(self):
        return f"{self.description} - {self.price_per_sqm} ₽ за м²"


class Document(models.Model):
    house = models.ForeignKey('House', on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=100, verbose_name='Название документа', blank=True)
    file = models.FileField(upload_to='documents/', verbose_name='Файл')

    @property
    def size(self):
        return round(self.file.size / (1024 * 1024), 2)

    def save(self, *args, **kwargs):
        if not self.title:
            self.title = os.path.basename(self.file.name).rsplit('.', 1)[0]
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.title} - {self.file.size} байт"



class FilterOption(models.Model):
    name = models.CharField(max_length=50)
    field_name = models.CharField(max_length=50,verbose_name="Имя поля из модели House")
    filter_type = models.CharField(max_length=50, choices=[('exact', 'Точное совпадение'), ('range', 'Диапазон'), ('contains', 'Содержит')])
    options = models.JSONField(default=dict)

    def __str__(self):
        return self.name



class Review(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True, default='Аноним')
    review = models.TextField()
    date = models.DateTimeField(default=timezone.now)
    rating = models.PositiveSmallIntegerField()
    file = models.FileField(upload_to='user/reviews/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = 'Аноним'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Отзыв от {self.name} с рейтингом {self.rating}"

    def get_file_name(self):
        return os.path.basename(self.file.name) if self.file else None

    def get_file_size(self):
        return round(self.file.size / (1024 * 1024), 2) if self.file else None


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает одобрения'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
    ]
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    house = models.ForeignKey('House', on_delete=models.CASCADE, verbose_name="Выбранный дом")
    finishing_option = models.ForeignKey('FinishingOption', on_delete=models.CASCADE, null=True, blank=True)
    construction_place = models.CharField(max_length=255)
    message = models.TextField()
    data_created = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус заказа")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="Широта")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="Долгота")

    def __str__(self):
        return f"Заказ от {self.name} на дом {self.house.title}"


class UserQuestion(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    house = models.ForeignKey('House', on_delete=models.CASCADE, verbose_name="Интересующий дом")
    question = models.TextField(verbose_name="Вопрос")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Вопрос от {self.name} по дому {self.house.title}"


class PurchasedHouse(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'В процессе'),
        ('completed', 'Построен'),
        ('not_started', 'Не начато'),
    ]

    house = models.ForeignKey(House, on_delete=models.CASCADE, verbose_name="Купленный дом")
    purchase_date = models.DateField(verbose_name="Дата покупки")
    buyer_name = models.CharField(max_length=255, verbose_name="Имя покупателя")
    buyer_phone = models.CharField(max_length=20, verbose_name="Номер телефона покупателя")
    buyer_email = models.EmailField(max_length=255, verbose_name="Почта покупателя")
    construction_status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name="Статус строительства")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="Широта")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="Долгота")


    def __str__(self):
        return f"{self.house.title} - {self.buyer_name}"