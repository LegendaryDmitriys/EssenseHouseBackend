import os

from django.core.validators import RegexValidator
from django.db import models
from django.utils.text import slugify
import random
from django.db.models import Count
from django.utils import timezone
import requests
from django.core.exceptions import ValidationError


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

class Filter(models.Model):
    name = models.CharField(max_length=50)
    value = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}: {self.value}"

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
    phone_validator = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Номер телефона должен содержать от 9 до 15 цифр, включая код страны."
    )

    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    house = models.ForeignKey('House', on_delete=models.CASCADE)
    finishing_option = models.ForeignKey('FinishingOption', on_delete=models.CASCADE)
    construction_place = models.CharField(max_length=255)
    message = models.TextField()
    data_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Заказ от {self.name} на дом {self.house.title}"

    def clean(self):
        super().clean()
        geocode_url = 'https://nominatim.openstreetmap.org/search'
        params = {'q': self.construction_place, 'format': 'json'}

        print(f"Запрос на очистку места строительства: {self.construction_place}")  # Логируем запрос

        try:
            response = requests.get(geocode_url, params=params, headers={'User-Agent': 'DjangoApp'})
            if response.status_code == 200:
                geo_data = response.json()
                if geo_data:
                    address = geo_data[0].get('address', {})
                    region = address.get('state', '')
                    county = address.get('county', '')

                    valid = False
                    if region and 'новгородская область' in region.lower():
                        valid = True
                    if county and 'новгородский район' in county.lower():
                        valid = True

                    if not valid:
                        print("Место строительства должно быть в Новгородской области или Новгородском районе.")  # Логируем предупреждение
                        raise ValidationError("Место строительства должно быть в Новгородской области или Новгородском районе.")
                else:
                    print("Место строительства не найдено через OpenStreetMap.")  # Логируем ошибку
                    raise ValidationError("Место строительства не найдено через OpenStreetMap.")
            else:
                print(f"Ошибка при запросе к OpenStreetMap: {response.status_code}")  # Логируем ошибку
                raise ValidationError(f"Ошибка при запросе к OpenStreetMap: {response.status_code}")
        except requests.RequestException as e:
            print(f"Ошибка соединения с OpenStreetMap: {e}")  # Логируем ошибку соединения