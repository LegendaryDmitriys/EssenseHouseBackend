from rest_framework import serializers
from .models import House, ConstructionTechnology, Filter, HouseCategory, HouseImage


class ConstructionTechnologySerializer(serializers.ModelSerializer):
    class Meta:
        model = ConstructionTechnology
        fields = ['id','name']

class HouseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseCategory
        fields = ['id', 'name', 'slug', 'short_description' , 'long_description']

class HouseImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseImage
        fields = ['id', 'image']


class HouseSerializer(serializers.ModelSerializer):
    # construction_technology = serializers.PrimaryKeyRelatedField(
    #     queryset=ConstructionTechnology.objects.all(),
    #     required=False,
    # )
    # category = serializers.PrimaryKeyRelatedField(
    #     queryset=HouseCategory.objects.all(),
    #     required=False,
    # )
    images = HouseImageSerializer(many=True)
    construction_technology = ConstructionTechnologySerializer(read_only=True)
    category = HouseCategorySerializer(read_only=True)

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

