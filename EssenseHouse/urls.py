
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from backend.views import HouseListView, HouseDetailView, ConstructionTechnologyListView, \
    ConstructionTechnologyDetailView, HouseCategoryListView, HouseCategoryDetailView, \
    FinishingOptionListView, FinishingOptionDetailView, DocumentListView, DocumentDetailView, ReviewsListView, \
    ReviewsDetailView, OrderListView, OrderDetailView, \
    FilteredHouseListView, PurchaseHouseListView, PurchaseHouseDetailView, FilterOptionListView, \
    UserQuestionHouseListView, UserQuestionHouseDetailView, UserQuestionListView, UserQuestionDetailView, \
    HouseCategoryDetailByIdView, FilterOptionDetailView, add_images_to_house, delete_image

urlpatterns = [
    path('houses/', HouseListView.as_view(), name='house_list'),
    path('houses/<int:pk>/', HouseDetailView.as_view(), name='house_detail'),
    path('houses/filter/', FilteredHouseListView.as_view(), name='filtered-house-list'),
    path('houses/purchase/', PurchaseHouseListView.as_view(), name='purchase_house_list'),
    path('houses/purchase/<int:pk>/', PurchaseHouseDetailView.as_view(), name='purchase_house_detail'),
    path('filter-options/', FilterOptionListView.as_view(), name='finishing-option-list'),
    path('filter-options/<int:pk>/', FilterOptionDetailView.as_view(), name='finishing-option-detail'),
    path('construction-technologies', ConstructionTechnologyListView.as_view(), name='construction_technology_list'),
    path('construction-technologies/<int:pk>', ConstructionTechnologyDetailView.as_view(), name='construction_technology_list'),
    path('category/', HouseCategoryListView.as_view(), name='category_list'),
    path('categories/<slug:slug>/', HouseCategoryDetailView.as_view(), name='house_by_category'),
    path('category/<int:pk>/', HouseCategoryDetailByIdView.as_view(), name='house_by_category'),
    path('finishing-options/', FinishingOptionListView.as_view(), name='finishing_options'),
    path('finishing-options/<int:pk>/', FinishingOptionDetailView.as_view(), name='finishing_options'),
    path('houses-document/', DocumentListView.as_view(), name='document_list'),
    path('house/documents/<int:pk>/', DocumentDetailView.as_view(), name='document_detail'),
    path('reviews/', ReviewsListView.as_view(), name='review_list'),
    path('reviews/<int:pk>/', ReviewsDetailView.as_view(), name='review_detail'),
    path('orders/', OrderListView.as_view(), name='order_list'),
    path('order/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('user-questions/', UserQuestionListView.as_view(), name='user_question_list'),
    path('user-question/<int:pk>/', UserQuestionDetailView.as_view(), name='user_question_detail'),
    path('user-questions/house/', UserQuestionHouseListView.as_view(), name='user_question_house_list'),
    path('user-question/house/<int:pk>/', UserQuestionHouseDetailView.as_view(), name='user_question_house_detail'),
    path('auth/', include('auth_app.urls')),
    path('mail/', include('mail_service.urls')),
    path('houses/<int:house_id>/images/', add_images_to_house, name='add_images_to_house'),
    path('images/<int:image_id>/delete/', delete_image, name='delete_image'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')),
    ]