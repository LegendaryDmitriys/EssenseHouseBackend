
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.cache import cache_page

from backend.views import HouseListView, HouseDetailView, ConstructionTechnologyListView, \
    ConstructionTechnologyDetailView, HouseCategoryListView, HouseCategoryDetailView, \
    FinishingOptionListView, FinishingOptionDetailView, DocumentListView, DocumentDetailView, ReviewsListView, \
    ReviewsDetailView, OrderListView, OrderDetailView, \
    FilteredHouseListView, PurchaseHouseListView, PurchaseHouseDetailView, FilterOptionListView, \
    UserQuestionHouseListView, UserQuestionHouseDetailView, UserQuestionListView, UserQuestionDetailView, \
    HouseCategoryDetailByIdView, FilterOptionDetailView, CreateHouseAPIView, UpdateHouseAPIView, DeleteImageView, \
    export_orders_to_excel, export_purchased_houses, export_user_questions_and_houses, DeleteDocumentView, \
    BlogListCreateView, BlogDetailView, BlogCategoryListView, BlogsByCategoryView

urlpatterns = [
    path('houses/', HouseListView.as_view(), name='house_list'),
    path('houses/<int:pk>/', HouseDetailView.as_view(), name='house_detail'),
    path('houses/filter/', FilteredHouseListView.as_view(), name='filtered-house-list'),
    path('purchase/', PurchaseHouseListView.as_view(), name='purchase_house_list'),
    path('purchase/<int:pk>/', PurchaseHouseDetailView.as_view(), name='purchase_house_detail'),
    path('filter-options/', FilterOptionListView.as_view(), name='finishing-option-list'),
    path('filter-options/<int:pk>/', cache_page(60 * 15)(FilterOptionDetailView.as_view()), name='finishing-option-detail'),
    path('construction-technologies', cache_page(60 * 15)(ConstructionTechnologyListView.as_view()), name='construction_technology_list'),
    path('construction-technologies/<int:pk>', cache_page(60 * 15)(ConstructionTechnologyDetailView.as_view()), name='construction_technology_list'),
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
    path('house-questions/', UserQuestionHouseListView.as_view(), name='user_question_house_list'),
    path('house-question/<int:pk>/', UserQuestionHouseDetailView.as_view(), name='user_question_house_detail'),
    path('auth/', include('auth_app.urls')),
    path('mail/', include('mail_service.urls')),
    path('houses/create', CreateHouseAPIView.as_view(), name='house_list-create'),
    path('houses/update/<int:house_id>/', UpdateHouseAPIView.as_view(), name='update_house'),
    path('houses/<int:house_id>/images/<int:image_id>/delete/<str:category>/', DeleteImageView.as_view(), name='delete_image'),
    path('houses/<int:house_id>/documents/<int:document_id>/delete/', DeleteDocumentView.as_view(), name='delete-document'),

    path('blogs/', BlogListCreateView.as_view(), name='post-list'),
    path('blogs/<int:pk>/', BlogDetailView.as_view(), name='post-detail'),
    path('blog/categories/', BlogCategoryListView.as_view(), name='category-list'),
    path('blog/categories/<int:category_id>/posts/', BlogsByCategoryView.as_view(), name='posts-by-category'),

    path('export_orders/', export_orders_to_excel, name='export_orders'),
    path('export_purchased_houses/', export_purchased_houses, name='export_purchased_houses'),
    path('export_user_questions_and_houses/', export_user_questions_and_houses, name='export_user_questions_and_houses'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')),
    ]