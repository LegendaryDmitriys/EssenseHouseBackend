from rest_framework import serializers
from .models import House, ConstructionTechnology, Filter, HouseCategory, HouseImage, HouseInteriorImage, \
    HouseFacadeImage, HouseLayoutImage, FinishingOption, Document, Review


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


class FilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Filter
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


