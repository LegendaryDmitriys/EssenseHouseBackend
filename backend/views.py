from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.views import APIView

from .models import House, ConstructionTechnology, Filter, HouseCategory, FinishingOption, Document, Review
from .serializer import HouseSerializer, ConstructionTechnologySerializer, FilterSerializer, HouseCategorySerializer, \
    FinishingOptionSerializer, DocumentSerializer, ReviewSerializer
from rest_framework.response import Response
from rest_framework import status


def filter_houses(filters):
    houses = House.objects.all()

    if 'price_min' in filters and 'price_max' in filters:
        min_price = int(filters.get('price_min'))
        max_price = int(filters.get('price_max'))
        houses = houses.filter(price__gte=min_price, price__lte=max_price)

    if 'bestSeller' in filters:
        houses = houses.filter(best_seller__in=filters.getlist('bestSeller'))

    if 'area_min' in filters and 'area_max' in filters:
        min_area = int(filters.get('area_min'))
        max_area = int(filters.get('area_max'))
        houses = houses.filter(area__gte=min_area, area__lte=max_area)

    if 'floors' in filters:
        houses = houses.filter(floors__in=filters.getlist('floors'))

    if 'rooms' in filters:
        houses = houses.filter(rooms__in=filters.getlist('rooms'))

    if 'living_area_min' in filters and 'living_area_max' in filters:
        min_living_area = int(filters.get('living_area_min'))
        max_living_area = int(filters.get('living_area_max'))
        houses = houses.filter(living_area__gte=min_living_area, living_area__lte=max_living_area)

    if 'bedrooms' in filters:
        houses = houses.filter(bedrooms__in=filters.getlist('bedrooms'))

    if 'garage' in filters:
        garage_value = True if 'Да' in filters.get('garage') else False
        houses = houses.filter(garage=garage_value)

    if 'purpose' in filters:
        houses = houses.filter(purpose__in=filters.getlist('purpose'))

    if 'constructionTechnology' in filters:
        houses = houses.filter(construction_technology__in=filters.getlist('constructionTechnology'))

    return houses


class HouseListView(APIView):
    serializer_class = HouseSerializer

    def get(self, request, id=None):
        if id is not None:
            try:
                house = House.objects.get(id=id)
                serializer = self.serializer_class(house)
                return Response(serializer.data)
            except House.DoesNotExist:
                return Response({'detail': 'Дом не найден.'}, status=status.HTTP_404_NOT_FOUND)


        category_slug = request.query_params.get('category')

        if category_slug:
            try:
                category = HouseCategory.objects.get(slug=category_slug)
                houses = House.objects.filter(category=category)
            except HouseCategory.DoesNotExist:
                return Response({'detail': 'Категория не найдена.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            houses = House.objects.all()

        serializer = self.serializer_class(houses, many=True)
        return Response(serializer.data)


class HouseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = House.objects.all()
    serializer_class = HouseSerializer


class ConstructionTechnologyListView(generics.ListCreateAPIView):
    queryset = ConstructionTechnology.objects.all()
    serializer_class = ConstructionTechnologySerializer


class ConstructionTechnologyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ConstructionTechnology.objects.all()
    serializer_class = ConstructionTechnologySerializer


class FilterListView(generics.ListCreateAPIView):
    queryset = Filter.objects.all()
    serializer_class = FilterSerializer


class FilterDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Filter.objects.all()
    serializer_class = FilterSerializer


class HouseCategoryListView(generics.ListCreateAPIView):
    queryset = HouseCategory.objects.all()
    serializer_class = HouseCategorySerializer


class HouseCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = HouseCategory.objects.all()
    serializer_class = HouseCategorySerializer
    lookup_field = 'slug'

    def get_queryset(self):
        category_slug = self.kwargs['slug']
        category = get_object_or_404(HouseCategory, slug=category_slug)
        return HouseCategory.objects.filter(slug=category_slug)



class FinishingOptionListView(generics.ListCreateAPIView):
    queryset = FinishingOption.objects.all()
    serializer_class = FinishingOptionSerializer


class FinishingOptionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FinishingOption.objects.all()
    serializer_class = FinishingOptionSerializer


class DocumentListView(generics.ListCreateAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer


class DocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer


class ReviewsListView(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


class ReviewsDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer