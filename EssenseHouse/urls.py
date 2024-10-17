
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from backend.views import HouseListView, HouseDetailView, ConstructionTechnologyListView, \
    ConstructionTechnologyDetailView, FilterListView, FilterDetailView, HouseCategoryListView, HouseCategoryDetailView, \
    FinishingOptionListView, FinishingOptionDetailView, DocumentListView, DocumentDetailView, ReviewsListView, \
    ReviewsDetailView

urlpatterns = [
    path('houses/', HouseListView.as_view(), name='house_list'),
    path('houses/<int:pk>/', HouseDetailView.as_view(), name='house_detail'),
    path('construction-technologies', ConstructionTechnologyListView.as_view(), name='construction_technology_list'),
    path('construction-technologies/<int:pk>', ConstructionTechnologyDetailView.as_view(), name='construction_technology_list'),
    path('filters/', FilterListView.as_view(), name='filter-list'),
    path('filters/<int:pk>/', FilterDetailView.as_view(), name='filter-detail'),
    path('category/', HouseCategoryListView.as_view(), name='category_list'),
    path('categories/<slug:slug>/', HouseCategoryDetailView.as_view(), name='house_by_category'),
    path('finishing-options/', FinishingOptionListView.as_view(), name='finishing_options'),
    path('finishing-options/<int:pk>/', FinishingOptionDetailView.as_view(), name='finishing_options'),
    path('houses-document/', DocumentListView.as_view(), name='document_list'),
    path('house/documents/<int:pk>/', DocumentDetailView.as_view(), name='document_detail'),
    path('reviews/', ReviewsListView.as_view(), name='review_list'),
    path('reviews/<int:pk>/', ReviewsDetailView.as_view(), name='review_detail'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)