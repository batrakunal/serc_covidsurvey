from django.urls import path
from . import views
from .views import SignUpView
from django.contrib.auth.views import LoginView
from django.conf.urls import include

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('profile/', views.get_user_profile, name = 'profile'),
    path('', include('django.contrib.auth.urls')),
]