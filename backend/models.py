from django.db import models
from django.utils.text import slugify

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
    bedrooms = models.PositiveIntegerField()
    garage = models.BooleanField(default=False)
    purpose = models.CharField(max_length=30, choices=PURPOSE_CHOICES)
    construction_technology = models.ForeignKey(ConstructionTechnology, on_delete=models.CASCADE)
    category = models.ForeignKey(HouseCategory, on_delete=models.CASCADE, related_name='houses')


    def __str__(self):
        return f"Дом {self.pk} - {self.price} руб."


class HouseImage(models.Model):
    house = models.ForeignKey(House, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='houses/')

    def __str__(self):
        return f"Изображение для дома {self.house.pk}"

class Filter(models.Model):
    name = models.CharField(max_length=50)
    value = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}: {self.value}"