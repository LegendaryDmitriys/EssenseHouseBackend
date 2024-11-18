import django_filters
from django.http import JsonResponse, Http404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import generics

from rest_framework.generics import ListCreateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from django.core.cache import cache

import openpyxl
from django.http import HttpResponse


from .models import House, ConstructionTechnology, HouseCategory, FinishingOption, Document, Review, Order, \
    UserQuestionHouse, PurchasedHouse, FilterOption, UserQuestion, Image

from .serializer import HouseSerializer, ConstructionTechnologySerializer, HouseCategorySerializer, \
    FinishingOptionSerializer, DocumentSerializer, ReviewSerializer, OrderSerializer, \
    PurchasedHouseSerializer, FilterOptionsSerializer, UserQuestionHouseSerializer, UserQuestionSerializer
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404



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


class HousePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class HouseListView(APIView):
    serializer_class = HouseSerializer
    parser_classes = [MultiPartParser, FormParser]
    pagination_class = HousePagination

    def get(self, request, id=None):
        if id is not None:
            return self.get_house_by_id(id)

        category_slug = request.query_params.get('category')
        filters = request.query_params
        sort_by = request.query_params.get('sort', 'priceAsc')

        houses = self.filter_houses(filters, category_slug, sort_by)

        paginator = self.pagination_class()
        paginated_houses = paginator.paginate_queryset(houses, request)
        serializer = self.serializer_class(paginated_houses, many=True)

        return paginator.get_paginated_response(serializer.data)

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
    queryset = House.objects.prefetch_related(
        'category',
        'construction_technology',
        'images',
        'interior_images',
        'facade_images',
        'layout_images',
        'finishing_options',
        'documents'
    ).all()
    serializer_class = HouseSerializer

    def get(self, request, *args, **kwargs):
        house = self.get_object()  # Извлекаем объект напрямую из базы
        house_data = HouseSerializer(house).data  # Сериализуем данные
        return Response(house_data)


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

    def get_queryset(self):
        options = cache.get('construction_technologies')
        if not options:
            options = super().get_queryset()
            cache.set('construction_technologies', options, timeout=60 * 60)
        return options


class ConstructionTechnologyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ConstructionTechnology.objects.all()
    serializer_class = ConstructionTechnologySerializer



class HouseCategoryListView(generics.ListCreateAPIView):
    queryset = HouseCategory.objects.prefetch_related('houses')
    serializer_class = HouseCategorySerializer

    def get_queryset(self):
        categories = cache.get('house_categories')
        if not categories:
            categories = super().get_queryset()
            cache.set('house_categories', categories, timeout=60 * 60)
        return categories

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


class HouseCategoryDetailByIdView(generics.RetrieveUpdateDestroyAPIView):
    queryset = HouseCategory.objects.all()
    serializer_class = HouseCategorySerializer


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


class UserQuestionListView(ListCreateAPIView):
    queryset = UserQuestion.objects.all()
    serializer_class = UserQuestionSerializer

    @method_decorator(cache_page(60 * 15))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class UserQuestionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserQuestion.objects.all()
    serializer_class = UserQuestionSerializer


class PurchaseHouseListView(generics.ListCreateAPIView):
    queryset = PurchasedHouse.objects.all()
    serializer_class = PurchasedHouseSerializer

    def get_queryset(self):
        construction_status = self.request.query_params.get('construction_status', None)

        queryset = PurchasedHouse.objects.all().select_related('house')


        queryset = queryset.prefetch_related('house__images', 'house__interior_images', 'house__facade_images', 'house__layout_images',
                                             'house__category', 'house__construction_technology', 'house__documents', 'house__finishing_options')

        if construction_status:
            return queryset.filter(construction_status=construction_status)
        return queryset


class PurchaseHouseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PurchasedHouse.objects.all()
    serializer_class = PurchasedHouseSerializer


class FilterOptionListView(generics.ListCreateAPIView):
    queryset = FilterOption.objects.all()
    serializer_class = FilterOptionsSerializer


class FilterOptionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FilterOption.objects.all()
    serializer_class = FilterOptionsSerializer


class CreateHouseAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, format=None):
        serializer = HouseSerializer(data=request.data)
        if serializer.is_valid():
            house = serializer.save()

            for file in request.FILES.getlist('images'):
                img = Image(image=file)
                img.save()
                house.images.add(img)

            for file in request.FILES.getlist('interior_images'):
                img = Image(image=file)
                img.save()
                house.interior_images.add(img)

            for file in request.FILES.getlist('facade_images'):
                img = Image(image=file)
                img.save()
                house.facade_images.add(img)

            for file in request.FILES.getlist('layout_images'):
                img = Image(image=file)
                img.save()
                house.layout_images.add(img)

            return Response({"message": "Дом успешно создан"}, status=201)
        return Response(serializer.errors, status=400)

class UpdateHouseAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def patch(self, request, house_id, format=None):
        try:
            house = House.objects.get(id=house_id)
        except House.DoesNotExist:
            return Response({"message": "Дом не найден"}, status=404)


        serializer = HouseSerializer(house, data=request.data, partial=True)
        if serializer.is_valid():
            house = serializer.save()

            if 'remove_images' in request.data:
                remove_images = request.data.getlist('remove_images')
                for image_id in remove_images:
                    try:
                        image = Image.objects.get(id=image_id)
                        house.images.remove(image)
                        image.delete()
                    except Image.DoesNotExist:
                        continue

            for file in request.FILES.getlist('images'):
                img = Image(image=file)
                img.save()
                house.images.add(img)

            for file in request.FILES.getlist('interior_images'):
                img = Image(image=file)
                img.save()
                house.interior_images.add(img)

            for file in request.FILES.getlist('facade_images'):
                img = Image(image=file)
                img.save()
                house.facade_images.add(img)

            for file in request.FILES.getlist('layout_images'):
                img = Image(image=file)
                img.save()
                house.layout_images.add(img)

            return Response({"message": "Дом успешно обновлен"}, status=200)

        return Response(serializer.errors, status=400)


class DeleteImageView(APIView):
    def delete(self, request, house_id, image_id, category):
        house = get_object_or_404(House, id=house_id)
        image = get_object_or_404(Image, id=image_id)


        if category == 'images':
            if image in house.images.all():
                house.images.remove(image)
        elif category == 'interior_images':
            if image in house.interior_images.all():
                house.interior_images.remove(image)
        elif category == 'facade_images':
            if image in house.facade_images.all():
                house.facade_images.remove(image)
        elif category == 'layout_images':
            if image in house.layout_images.all():
                house.layout_images.remove(image)
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid category'}, status=400)


        if image.houses.count() == 0:
            image.delete()

        return JsonResponse({'status': 'success', 'message': 'Image deleted successfully'})


def export_orders_to_excel(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Orders"

    headers = [
        "ID", "Название дома", "Покупатель", "Телефон", "Email",
        "Место строительства", "Отделка", "Дата заказа", "Статус"
    ]
    ws.append(headers)

    orders = Order.objects.all()

    for order in orders:
        row = [
            order.id,
            order.house.title if order.house else "Не указано",
            order.name,
            order.phone,
            order.email,
            order.construction_place,
            order.finishing_option.title if order.finishing_option else "Не указано",
            order.data_created.strftime('%Y-%m-%d'),  # Форматируем дату
            order.status
        ]
        ws.append(row)


    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=orders.xlsx'

    wb.save(response)

    return response

def export_purchased_houses(request):
    purchased_houses = PurchasedHouse.objects.all()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Purchased Houses"

    ws.append([
        "Дом",
        "Дата покупки",
        "Покупатель",
        "Телефон",
        "Почта",
        "Статус строительства",
        "Широта",
        "Долгота",
    ])

    for house in purchased_houses:
        ws.append([
            house.house.title,
            house.purchase_date,
            house.buyer_name,
            house.buyer_phone,
            house.buyer_email,
            house.construction_status,
            house.latitude if house.latitude else "Не указано",
            house.longitude if house.longitude else "Не указано",
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="purchased_houses.xlsx"'

    wb.save(response)
    return response

def export_user_questions_and_houses(request):
    user_questions = UserQuestion.objects.all()
    user_question_houses = UserQuestionHouse.objects.all()


    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "User Questions and Houses"

    ws.append([
        "Имя",
        "Телефон",
        "Дата создания",
        "Статус"
    ])

    for question in user_questions:
        ws.append([
            question.name,
            question.phone,
            question.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            question.status,
        ])


    ws.append([])

    ws.append([
        "Имя",
        "Телефон",
        "Email",
        "Дом",
        "Вопрос",
        "Дата создания",
        "Статус"
    ])

    for question_house in user_question_houses:
        ws.append([
            question_house.name,
            question_house.phone,
            question_house.email,
            question_house.house.title,
            question_house.question,
            question_house.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            question_house.status,
        ])


    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="user_questions_and_houses.xlsx"'

    wb.save(response)
    return response