from django.utils import timezone
from django.core.validators import RegexValidator
from rest_framework import serializers
import requests
from django.core.exceptions import ValidationError

from .models import House, ConstructionTechnology, HouseCategory \
    , FinishingOption, Document, Review, Order, PurchasedHouse, \
    FilterOption, UserQuestionHouse, UserQuestion, HouseFinishing, Image


class ConstructionTechnologySerializer(serializers.ModelSerializer):
    class Meta:
        model = ConstructionTechnology
        fields = ['id','name']



class HouseCategorySerializer(serializers.ModelSerializer):
    random_image_url = serializers.SerializerMethodField()
    class Meta:
        model = HouseCategory
        fields = ['id', 'name', 'slug', 'short_description' , 'long_description', 'random_image_url']

    def get_random_image_url(self, obj):
        return obj.get_random_image()


class FinishingOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinishingOption
        fields = ['id', 'title', 'description', 'image', 'price_per_sqm']

    def create(self, validated_data):
        return FinishingOption.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.price_per_sqm = validated_data.get('price_per_sqm', instance.price_per_sqm)

        image = validated_data.get('image', None)
        if image:

            instance.image = image

        instance.save()
        return instance

class HouseFinishingSerializer(serializers.ModelSerializer):
    finishing_option = FinishingOptionSerializer(read_only=True)

    class Meta:
        model = HouseFinishing
        fields = "__all__"


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'file', 'title', 'size']


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'image']


class HouseSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, required=False)
    interior_images = ImageSerializer(many=True, required=False)
    facade_images = ImageSerializer(many=True, required=False)
    layout_images = ImageSerializer(many=True, required=False)
    documents = DocumentSerializer(many=True, required=False)
    new_price = serializers.SerializerMethodField()
    discount = serializers.SerializerMethodField()
    garage = serializers.IntegerField(allow_null=True, required=False)

    def get_new_price(self, obj):
        return round(obj.new_price) if obj.new_price else None

    def get_discount(self, obj):
        return obj.discount


    construction_technology = serializers.PrimaryKeyRelatedField(
        queryset=ConstructionTechnology.objects.all(), write_only=True
    )
    category = serializers.PrimaryKeyRelatedField(
        queryset=HouseCategory.objects.all(), write_only=True
    )
    finishing_options = serializers.PrimaryKeyRelatedField(
        queryset=FinishingOption.objects.all(), many=True, write_only=True
    )

    construction_technology_details = ConstructionTechnologySerializer(
        read_only=True, source='construction_technology'
    )
    category_details = HouseCategorySerializer(
        read_only=True, source='category'
    )
    finishing_options_details = FinishingOptionSerializer(
        read_only=True, many=True, source='finishing_options'
    )


    class Meta:
        model = House
        fields = '__all__'

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        interior_images_data = validated_data.pop('interior_images', [])
        facade_images_data = validated_data.pop('facade_images', [])
        layout_images_data = validated_data.pop('layout_images', [])
        finishing_options_data = validated_data.pop('finishing_options', [])
        documents_data = validated_data.pop('documents', [])

        house = House.objects.create(**validated_data)

        for image_data in images_data:
            house.images.add(Image.objects.create(image=image_data['image']))

        for image_data in interior_images_data:
            house.interior_images.add(Image.objects.create(image=image_data['image']))

        for image_data in facade_images_data:
            house.facade_images.add(Image.objects.create(image=image_data['image']))

        for image_data in layout_images_data:
            house.layout_images.add(Image.objects.create(image=image_data['image']))

        house.finishing_options.set(finishing_options_data)

        for document_data in documents_data:
            Document.objects.create(house=house, **document_data)

        return house

class FilterOptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FilterOption
        fields = '__all__'


def validate_file_type(value):
    allowed_mime_types = [
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'image/jpeg',
        'image/png',
        'image/gif',
    ]

    if value.content_type not in allowed_mime_types:
        raise ValidationError("Разрешены только файлы Word, Excel или изображения (JPG, PNG, GIF).")

    allowed_extensions = ['.doc', '.docx', '.xls', '.xlsx', '.jpg', '.jpeg', '.png', '.gif']
    if not any(value.name.endswith(ext) for ext in allowed_extensions):
        raise ValidationError("Разрешены только файлы с расширениями: .doc, .docx, .xls, .xlsx, .jpg, .jpeg, .png, .gif.")


class ReviewSerializer(serializers.ModelSerializer):
    file = serializers.FileField(validators=[validate_file_type], required=False)
    file_name = serializers.SerializerMethodField()
    file_size = serializers.SerializerMethodField()
    class Meta:
        model = Review
        fields = ['id', 'name', 'review', 'date', 'rating', 'file', 'file_name', 'file_size', 'status']

    def get_file_name(self, obj):
        return obj.get_file_name()

    def get_file_size(self, obj):
        return obj.get_file_size()



class OrderSerializer(serializers.ModelSerializer):
    house = serializers.PrimaryKeyRelatedField(queryset=House.objects.all(), required=True)
    finishing_option = serializers.SerializerMethodField(read_only=True)

    house_details = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = '__all__'
        extra_kwargs = {
            'name': {'required': False},
            'phone': {'required': False},
            'construction_place': {'required': False},
            'message': {'required': False},
            'house': {'required': True},
        }

    def get_house_details(self, obj):
        return {
            "id": obj.house.id,
            "title": obj.house.title,
        }

    def get_finishing_option(self, obj):
        if obj.finishing_option:
            return {
                "id": obj.finishing_option.id,
                "title": obj.finishing_option.title,
            }
        return None

    def validate_phone(self, value):
        phone_validator = RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Номер телефона должен содержать от 9 до 15 цифр, включая код страны."
        )
        try:
            phone_validator(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.message)
        return value

    def validate_construction_place(self, value):
        if not value.lower().startswith("новгородская область"):
            raise ValidationError("Место строительства должно начинаться с 'Новгородская область'.")

        geocode_url = 'https://nominatim.openstreetmap.org/search'
        params = {'q': value, 'format': 'json'}

        try:
            response = requests.get(geocode_url, params=params, headers={'User-Agent': 'DjangoApp'})
            if response.status_code == 200:
                geo_data = response.json()
                if geo_data:
                    display_name = geo_data[0].get('display_name', '')
                    lat = geo_data[0].get('lat')
                    lon = geo_data[0].get('lon')

                    if 'новгородская область' not in display_name.lower():
                        raise ValidationError("Место строительства должно находиться в пределах Новгородской области.")

                    self.latitude = lat
                    self.longitude = lon
                else:
                    raise ValidationError("Место строительства не найдено через OpenStreetMap.")
            else:
                raise ValidationError(f"Ошибка при запросе к OpenStreetMap: {response.status_code}")
        except requests.RequestException as e:
            raise ValidationError(f"Ошибка соединения с OpenStreetMap: {e}")

        return value

    def create(self, validated_data):
        validated_data['latitude'] = getattr(self, 'latitude', None)
        validated_data['longitude'] = getattr(self, 'longitude', None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        previous_status = instance.status
        new_status = validated_data.get('status', instance.status)

        if new_status == 'approved' and (not instance.latitude or not instance.longitude):
            raise ValidationError({
                "detail": "Невозможно подтвердить заказ без указания широты и долготы."
            })


        instance.latitude = validated_data.get('latitude', getattr(self, 'latitude', instance.latitude))
        instance.longitude = validated_data.get('longitude', getattr(self, 'longitude', instance.longitude))

        if previous_status != 'approved' and new_status == 'approved':
            PurchasedHouse.objects.create(
                house=instance.house,
                purchase_date=timezone.now().date(),
                buyer_name=instance.name,
                buyer_phone=instance.phone,
                buyer_email=instance.email,
                construction_status='not_started',
                latitude=instance.latitude,
                longitude=instance.longitude,
            )

        instance = super().update(instance, validated_data)
        return instance


class UserQuestionHouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserQuestionHouse
        fields = '__all__'

    def validate_phone(self, value):
        phone_validator = RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Номер телефона должен содержать от 9 до 15 цифр, включая код страны."
        )
        try:
            phone_validator(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.message)
        return value


class UserQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserQuestion
        fields = '__all__'

    def validate_phone(self, value):
        phone_validator = RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Номер телефона должен содержать от 9 до 15 цифр, включая код страны."
        )
        try:
            phone_validator(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.message)
        return value


class PurchasedHouseSerializer(serializers.ModelSerializer):
    house = HouseSerializer(read_only=True)
    house_id = serializers.PrimaryKeyRelatedField(queryset=House.objects.all(), source='house')
    class Meta:
        model = PurchasedHouse
        fields = '__all__'

