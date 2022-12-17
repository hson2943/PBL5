from django.urls import path
from .views import *
from django.contrib.auth import views as auth_view

urlpatterns = [
    path('home/', get_all_url_img),
    path('logout/',auth_view.LogoutView.as_view(next_page='/'),name='logout'),
    path('', auth_view.LoginView.as_view(template_name='login.html'), name='login'),
    path('statistic/',get_all_img, name = 'statistic'),    
    path('<str:key>/detail', detail, name = 'detail'),
    path('<str:name_img>/detail_img',detail_img, name = 'detail_img')
]