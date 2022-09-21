from django.contrib import admin
from django.urls import path
from . import views
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import re_path as url
from django.contrib.staticfiles.storage import staticfiles_storage

app_name = "core"
urlpatterns = [
    path('home/',views.home,name = 'home'),
    path('email/', views.email, name = 'email'),
    path('login/', views.loginpage, name = 'login'),
    path('register/', views.register, name = 'register'),
    path('', views.register, name = 'register'),
    path('company_list/', views.company_list, name = 'company_list'),
    #path('simple_function/',views.simple_function, name='simple_function'),
    url(r'^media/(?P<path>.*)$', serve,{'document_root':       settings.MEDIA_ROOT}), 
    url(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}), 
]