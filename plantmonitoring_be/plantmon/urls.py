from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from plantmon import views

urlpatterns = [
    path('users/register', views.UserRegister.as_view()),
    path('users/<uuid:pk>', views.UserDetail.as_view()),
    path('devices/<uuid:pk>', views.DeviceDetail.as_view()),
    path('devices/', views.DeviceCreate.as_view()),
    path('api-auth', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api-auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
