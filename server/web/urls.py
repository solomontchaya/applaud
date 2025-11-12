from django.urls import path
from web import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='index'),
    path('auth/', views.SignInView.as_view(), name='signin'),
    path('auth/signup/', views.SignUpView.as_view(), name='signup'),
    path('auth/signout/', views.SignOutView.as_view(), name='signout'),
]