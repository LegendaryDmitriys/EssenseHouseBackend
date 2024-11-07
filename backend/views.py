import django_filters
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.views import APIView

from .models import House, ConstructionTechnology, HouseCategory, FinishingOption, Document, Review, Order, \
    UserQuestionHouse, PurchasedHouse, FilterOption, UserQuestion
from .serializer import HouseSerializer, ConstructionTechnologySerializer, HouseCategorySerializer, \
    FinishingOptionSerializer, DocumentSerializer, ReviewSerializer, OrderSerializer, \
    PurchasedHouseSerializer, FilterOptionsSerializer, UserQuestionHouseSerializer, UserQuestionSerializer
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters



def filter_houses(filters, category=None):
    houses = House.objects.filter(category=category) if category else House.objects.all()

    if 'price_min' in filters and filters['price_min']:
        min_price = int(filters['price_min'])
        houses = houses.filter(price__gte=min_price)

    if 'price_max' in filters and filters['price_max']:
        max_price = int(filters['price_max'])
        houses = houses.filter(price__lte=max_price)

    if 'bestSeller' in filters and filters.getlist('bestSeller'):
        houses = houses.filter(best_seller__in=filters.getlist('bestSeller'))

    if 'area_min' in filters and filters['area_min']:
        min_area = int(filters['area_min'])
        houses = houses.filter(area__gte=min_area)

    if 'area_max' in filters and filters['area_max']:
        max_area = int(filters['area_max'])
        houses = houses.filter(area__lte=max_area)

    if 'floors' in filters and filters.getlist('floors'):
        houses = houses.filter(floors__in=filters.getlist('floors'))

    if 'rooms' in filters and filters.getlist('rooms'):
        houses = houses.filter(rooms__in=filters.getlist('rooms'))

    if 'living_area_min' in filters and filters['living_area_min']:
        min_living_area = int(filters['living_area_min'])
        houses = houses.filter(living_area__gte=min_living_area)

    if 'living_area_max' in filters and filters['living_area_max']:
        max_living_area = int(filters['living_area_max'])
        houses = houses.filter(living_area__lte=max_living_area)

    if 'bedrooms' in filters and filters.getlist('bedrooms'):
        houses = houses.filter(bedrooms__in=filters.getlist('bedrooms'))

    if 'garage' in filters:
        garage_value = True if filters['garage'] == 'Да' else False
        houses = houses.filter(garage=garage_value)

    if 'purpose' in filters and filters.getlist('purpose'):
        houses = houses.filter(purpose__in=filters.getlist('purpose'))

    if 'constructionTechnology' in filters and filters.getlist('constructionTechnology'):
        houses = houses.filter(construction_technology__in=filters.getlist('constructionTechnology'))

    return houses


class DynamicHouseFilter(django_filters.FilterSet):
    class Meta:
        model = House
        fields = {}

class HouseListView(APIView):
    serializer_class = HouseSerializer

    def get(self, request, id=None):
        if id is not None:
            return self.get_house_by_id(id)

        category_slug = request.query_params.get('category')
        filters = request.query_params
        sort_by = request.query_params.get('sort', 'priceAsc')

        houses = self.filter_houses(filters, category_slug, sort_by)

        serializer = self.serializer_class(houses, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_house_by_id(self, id):
        try:
            house = House.objects.get(id=id)
            serializer = self.serializer_class(house)
            return Response(serializer.data)
        except House.DoesNotExist:
            return Response({'detail': 'Дом не найден.'}, status=status.HTTP_404_NOT_FOUND)

    def filter_houses(self, filters, category_slug=None, sort_by='priceAsc'):
        houses = House.objects.all()

        if category_slug:
            try:
                category = HouseCategory.objects.get(slug=category_slug)
                houses = houses.filter(category=category)
            except HouseCategory.DoesNotExist:
                return House.objects.none()

        filtered_houses = self.create_dynamic_filter(filters, houses)

        if sort_by == 'priceAsc':
            filtered_houses = filtered_houses.order_by('price')
        elif sort_by == 'priceDesc':
            filtered_houses = filtered_houses.order_by('-price')
        elif sort_by == 'popularityAsc':
            filtered_houses = filtered_houses.order_by('popularity')
        elif sort_by == 'popularityDesc':
            filtered_houses = filtered_houses.order_by('-popularity')

        return filtered_houses

    def create_dynamic_filter(self, filters, queryset):
        filters_db = FilterOption.objects.all()
        filter_dict = {}

        for filter_option in filters_db:
            if filter_option.filter_type == 'exact':
                filter_dict[filter_option.field_name] = django_filters.CharFilter(field_name=filter_option.field_name)
            elif filter_option.filter_type == 'range':
                filter_dict[filter_option.field_name + '__gte'] = django_filters.NumberFilter(
                    field_name=filter_option.field_name, lookup_expr='gte')
                filter_dict[filter_option.field_name + '__lte'] = django_filters.NumberFilter(
                    field_name=filter_option.field_name, lookup_expr='lte')
            elif filter_option.filter_type == 'contains':
                filter_dict[filter_option.field_name] = django_filters.CharFilter(
                    field_name=filter_option.field_name, lookup_expr='icontains')

        house_filter = DynamicHouseFilter(filters, queryset=queryset)
        house_filter.filters.update(filter_dict)

        return house_filter.qs


class HouseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = House.objects.all()
    serializer_class = HouseSerializer



class FilteredHouseListView(APIView):
    serializer_class = HouseSerializer

    def get(self, request):
        filters = request.query_params

        houses = filter_houses(filters)
        serializer = self.serializer_class(houses, many=True)
        return Response(serializer.data)



class ConstructionTechnologyListView(generics.ListCreateAPIView):
    queryset = ConstructionTechnology.objects.all()
    serializer_class = ConstructionTechnologySerializer


class ConstructionTechnologyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ConstructionTechnology.objects.all()
    serializer_class = ConstructionTechnologySerializer

#
# class DynamicHouseFilter(django_filters.FilterSet):
#     class Meta:
#         model = House
#         fields = {}
#
# class FilterListView(APIView):
#     def get(self, request):
#         filters_db = FilterOption.objects.all()
#         filter_dict = {}
#
#         for filter_option in filters_db:
#             if filter_option.filter_type == 'exact':
#                 filter_dict[filter_option.field_name] = django_filters.CharFilter(field_name=filter_option.field_name)
#             elif filter_option.filter_type == 'range':
#                 filter_dict[filter_option.field_name + '__gte'] = django_filters.NumberFilter(
#                     field_name=filter_option.field_name, lookup_expr='gte')
#                 filter_dict[filter_option.field_name + '__lte'] = django_filters.NumberFilter(
#                     field_name=filter_option.field_name, lookup_expr='lte')
#             elif filter_option.filter_type == 'contains':
#                 filter_dict[filter_option.field_name] = django_filters.CharFilter(
#                     field_name=filter_option.field_name, lookup_expr='icontains')
#
#         house_filter = DynamicHouseFilter(request.GET, queryset=House.objects.all())
#         house_filter.filters.update(filter_dict)
#
#
#         filtered_houses = house_filter.qs
#
#
#         serializer = HouseSerializer(filtered_houses, many=True)
#         return Response(serializer.data)


class HouseCategoryListView(generics.ListCreateAPIView):
    queryset = HouseCategory.objects.all()
    serializer_class = HouseCategorySerializer


class HouseCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = HouseCategory.objects.all()
    serializer_class = HouseCategorySerializer
    lookup_field = 'slug'

    def get(self, request, *args, **kwargs):
        category_slug = self.kwargs['slug']
        category = get_object_or_404(HouseCategory, slug=category_slug)

        filters = request.query_params
        houses = filter_houses(filters, category=category)

        serializer = HouseSerializer(houses, many=True)
        return Response(serializer.data)



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

    def get_queryset(self):
        status = self.request.query_params.get('status', None)

        if status:
            return Review.objects.filter(status=status)
        return Review.objects.all()


class ReviewsDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


class OrderListView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class UserQuestionHouseListView(generics.ListCreateAPIView):
    queryset = UserQuestionHouse.objects.all()
    serializer_class = UserQuestionHouseSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserQuestionHouseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserQuestionHouse.objects.all()
    serializer_class = UserQuestionHouseSerializer


class UserQuestionListView(generics.ListCreateAPIView):
    queryset = UserQuestion.objects.all()
    serializer_class = UserQuestionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserQuestionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserQuestion.objects.all()
    serializer_class = UserQuestionSerializer


class PurchaseHouseListView(generics.ListCreateAPIView):
    queryset = PurchasedHouse.objects.all()
    serializer_class = PurchasedHouseSerializer

    def get_queryset(self):
        construction_status = self.request.query_params.get('construction_status', None)

        if construction_status:
            return PurchasedHouse.objects.filter(construction_status=construction_status)
        return PurchasedHouse.objects.all()


class PurchaseHouseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PurchasedHouse.objects.all()
    serializer_class = PurchasedHouseSerializer


class FilterOptionListView(generics.ListCreateAPIView):
    queryset = FilterOption.objects.all()
    serializer_class = FilterOptionsSerializer


