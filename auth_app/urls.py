from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import RegisterView, LoginView, UserDetailView, CurrentUserView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='admin_register'),
    path('login/', LoginView.as_view(), name='admin_login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    # path('users/<int:user_id>/', UserDetailView.as_view(), name='user-detail'),
    path('users/me/', CurrentUserView.as_view()),
]
