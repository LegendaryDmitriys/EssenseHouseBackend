import os

from django.db import models
from django.utils.text import slugify
from django.db.models import Count
from django.utils import timezone

from auth_app.models import User


class HouseCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    short_description = models.TextField(null=True, blank=True)
    long_description = models.TextField(null=True, blank=True)
    slug = models.SlugField(unique=True, blank=True, db_index=True)

    class Meta:
        verbose_name = "Категория дома"
        verbose_name_plural = "Категории домов"
        indexes = [
            models.Index(fields=['name']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_random_image(self):
        house_with_images = self.houses.annotate(num_images=Count('images')).filter(num_images__gt=0).first()
        return house_with_images.images.first().image.url if house_with_images else None


class ConstructionTechnology(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class House(models.Model):
    BESTSELLER_CHOICES = [
        ('Акция', 'Акция'),
    ]

    PURPOSE_CHOICES = [
        ('Частный дом', 'Частный дом'),
        ('Коммерческая недвижимость', 'Коммерческая недвижимость'),
    ]

    title = models.CharField(max_length=100, unique=False, db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, db_index=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                              verbose_name="Скидка (%)")
    new = models.BooleanField(default=True, verbose_name="Новый продукт", db_index=True)
    best_seller = models.CharField(max_length=10, choices=BESTSELLER_CHOICES, blank=True, null=True, db_index=True)
    area = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Площадь, м²", db_index=True)
    floors = models.PositiveIntegerField(verbose_name="Количество этажей", db_index=True)
    rooms = models.PositiveIntegerField(verbose_name="Количество комнат", db_index=True)
    living_area = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Жилая площадь, м²", db_index=True)
    kitchen_area = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Площадь кухни",db_index=True)
    bedrooms = models.PositiveIntegerField(verbose_name="Количество спален", db_index=True)
    bathrooms = models.PositiveIntegerField(verbose_name="Количество санузлов", null=True, blank=True, db_index=True)
    garage = models.IntegerField(verbose_name="Гараж (кол-во машин)", null=True, blank=True)
    purpose = models.CharField(max_length=30, choices=PURPOSE_CHOICES)
    warranty = models.PositiveIntegerField(verbose_name="Гарантия, лет", null=True, blank=True)
    construction_time = models.PositiveIntegerField(verbose_name="Срок строительства, дней", null=True, blank=True)
    construction_technology = models.ForeignKey(ConstructionTechnology, on_delete=models.CASCADE, db_index=True)
    category = models.ForeignKey(HouseCategory, on_delete=models.CASCADE, related_name='houses', db_index=True)
    description = models.TextField(verbose_name="Описание", null=True, blank=True)
    finishing_options = models.ManyToManyField('FinishingOption', through='HouseFinishing', related_name='houses', db_index=True)
    images = models.ManyToManyField('Image', related_name='houses', blank=True)
    interior_images = models.ManyToManyField('Image', related_name='interior_houses', blank=True)
    facade_images = models.ManyToManyField('Image', related_name='facade_houses', blank=True)
    layout_images = models.ManyToManyField('Image', related_name='layout_houses', blank=True)
    documents = models.ManyToManyField('Document', related_name='houses', blank=True)

    def __str__(self):
        return f"Дом {self.pk} - {self.price} руб."

    @property
    def new_price(self):
        if self.discount_percentage:
            return self.price * (1 - self.discount_percentage / 100)
        return None

    @property
    def discount(self):
        if self.discount_percentage:
            return self.discount_percentage
        return None


class Image(models.Model):
    image = models.ImageField(upload_to='house_images/')


class FinishingOption(models.Model):
    title = models.CharField(max_length=100, verbose_name='Заголовок')
    description = models.TextField(verbose_name="Описание")
    price_per_sqm = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена за м²", null=True, blank=True)
    image = models.ImageField(upload_to='houses/finishing_options/', verbose_name='Изображение', null=True, blank=True)

    def __str__(self):
        return f"{self.description} - {self.price_per_sqm} ₽ за м²"


class HouseFinishing(models.Model):
    house = models.ForeignKey('House', on_delete=models.CASCADE)
    finishing_option = models.ForeignKey('FinishingOption', on_delete=models.CASCADE)

    def __str__(self):
        return f"Отделка {self.finishing_option.title} для дома {self.house.title}"

class Document(models.Model):
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
    STATUS_CHOICES = [
        ('published', 'Опубликован'),
        ('pending', 'Ожидает публикации'),
        ('rejected', 'Отказано'),
    ]

    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    review = models.TextField()
    date = models.DateTimeField(default=timezone.now)
    rating = models.PositiveSmallIntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Отзыв от {self.name} с рейтингом {self.rating}"


class ReviewFile(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="files")
    file = models.FileField(upload_to='user/reviews/')
    file_type = models.CharField(max_length=50, choices=[
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('text', 'Text'),
        ('document', 'Document'),
        ('msword', 'Microsoft Word'),
        ('wordprocessingml', 'Word Processing ML'),
    ], default='document')

    def get_file_name(self):
        return os.path.basename(self.file.name)

    def get_file_size(self):
        return round(self.file.size / (1024 * 1024), 2)





class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает одобрения'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
    ]
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Пользователь")
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    house = models.ForeignKey('House', on_delete=models.CASCADE, verbose_name="Выбранный дом",db_index=True)
    finishing_option = models.ForeignKey('FinishingOption', on_delete=models.CASCADE, null=True, blank=True)
    construction_place = models.CharField(max_length=255)
    message = models.TextField()
    data_created = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус заказа")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="Широта")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="Долгота")

    def __str__(self):
        return f"Заказ от {self.name} на дом {self.house.title}"


class UserQuestionHouse(models.Model):
    STATUS_CHOICES = [
        ('waiting', 'Ожидает ответа'),
        ('answered', 'Ответ предоставлен'),
        ('closed', 'Закрыт'),
    ]
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Пользователь")
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    house = models.ForeignKey('House', on_delete=models.CASCADE, verbose_name="Интересующий дом")
    question = models.TextField(verbose_name="Вопрос")
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='waiting')

    def __str__(self):
        return f"Вопрос от {self.first_name} {self.last_name} по дому {self.house.title}"


class UserQuestion(models.Model):
    STATUS_CHOICES = [
        ('waiting', 'Ожидает ответа'),
        ('answered', 'Ответ предоставлен'),
        ('closed', 'Закрыт'),
    ]
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Пользователь")
    first_name = models.CharField(max_length=255, verbose_name="Имя")
    last_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='waiting', verbose_name="Статус")

    def __str__(self):
        return f"Запрос от {self.first_name} {self.last_name} ({self.phone})"


class PurchasedHouse(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'В процессе'),
        ('completed', 'Построен'),
        ('not_started', 'Не начато'),
    ]
    house = models.ForeignKey(House, on_delete=models.CASCADE, verbose_name="Купленный дом",db_index=True)
    purchase_date = models.DateTimeField(verbose_name="Дата покупки")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Пользователь")
    first_name = models.CharField(max_length=255, verbose_name="Имя покупателя")
    last_name = models.CharField(max_length=255, verbose_name="Фамилия покупателя")
    phone_number = models.CharField(max_length=20, verbose_name="Номер телефона покупателя")
    email = models.EmailField(max_length=255, verbose_name="Почта покупателя")
    construction_status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name="Статус строительства")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="Широта")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="Долгота")
    address = models.CharField(max_length=255, verbose_name="Адрес строительства", null=True, blank=True)
    completed_date = models.DateTimeField(verbose_name="Дата завершения строительства", null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.construction_status == 'completed' and not self.completed_date:
            self.completed_date = timezone.now().date()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.house.title} - {self.buyer_name}"


class BlogCategory(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Категория")

    def __str__(self):
        return self.name


class Blog(models.Model):
    STATUS_CHOICES = [
        ('published', 'Опубликован'),
        ('pending', 'Ожидает публикации'),
        ('rejected', 'Отказано'),
    ]
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    description = models.TextField(verbose_name="Описание")
    content = models.TextField(verbose_name="Содержимое")
    date = models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")
    image = models.ImageField(upload_to='blog/', verbose_name="Изображение")
    category = models.ForeignKey(BlogCategory, on_delete=models.CASCADE, related_name="blogs", verbose_name="Категория")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name="Статус строительства")

    def __str__(self):
        return self.title