from django.utils import timezone
from django.core.validators import RegexValidator
from rest_framework import serializers
import requests
from django.core.exceptions import ValidationError


from .models import House, ConstructionTechnology, HouseCategory, HouseImage, HouseInteriorImage, \
    HouseFacadeImage, HouseLayoutImage, FinishingOption, Document, Review, Order, UserQuestion, PurchasedHouse, \
    FilterOption


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

class HouseImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseImage
        fields = ['id', 'image']

class HouseInteriorImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseInteriorImage
        fields = ['id', 'image']


class HouseFacadeImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseFacadeImage
        fields = ['id', 'image']


class HouseLayoutImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseLayoutImage
        fields = ['id', 'image']


class FinishingOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinishingOption
        fields = ['id', 'title', 'description', 'image', 'price_per_sqm']


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'file', 'title', 'size']


class HouseSerializer(serializers.ModelSerializer):
    images = HouseImageSerializer(many=True)
    interior_images = HouseInteriorImageSerializer(many=True)
    facade_images = HouseFacadeImageSerializer(many=True)
    layout_images = HouseLayoutImageSerializer(many=True)
    construction_technology = ConstructionTechnologySerializer(read_only=True)
    category = HouseCategorySerializer(read_only=True)
    finishing_options = FinishingOptionSerializer(many=True, read_only=True)
    documents = DocumentSerializer(many=True, read_only=True)

    class Meta:
        model = House
        fields = '__all__'


    def create(self, validated_data):
        images_data = validated_data.pop('images')
        house = House.objects.create(**validated_data)
        for image_data in images_data:
            HouseImage.objects.create(house=house, **image_data)
        return house

    def update(self, instance, validated_data):
        images_data = validated_data.pop('images', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if images_data is not None:

            instance.images.all().delete()


            for image_data in images_data:
                HouseImage.objects.create(house=instance, **image_data)

        return instance


class FilterOptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FilterOption
        fields = '__all__'



class ReviewSerializer(serializers.ModelSerializer):
    file_name = serializers.SerializerMethodField()
    file_size = serializers.SerializerMethodField()
    class Meta:
        model = Review
        fields = ['id', 'name', 'review', 'date', 'rating', 'file', 'file_name', 'file_size']

    def get_file_name(self, obj):
        return obj.get_file_name()

    def get_file_size(self, obj):
        return obj.get_file_size()



class OrderSerializer(serializers.ModelSerializer):
    finishing_options = FinishingOptionSerializer(read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
        extra_kwargs = {
            'name': {'required': False},
            'phone': {'required': False},
            'construction_place': {'required': False},
            'message': {'required': False},
            'house': {'required': False},
        }

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

                    print(f"Полное название: {display_name}")
                    print(f"Широта: {lat}, Долгота: {lon}")

                    if 'новгородская область' not in display_name.lower():
                        raise ValidationError("Место строительства должно находиться в пределах Новгородской области.")

                    # Добавляем широту и долготу в validated_data
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

        instance.latitude = getattr(self, 'latitude', instance.latitude)
        instance.longitude = getattr(self, 'longitude', instance.longitude)


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

            if 'status' in validated_data:
                instance.status = new_status

            instance.save()
            return instance


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

