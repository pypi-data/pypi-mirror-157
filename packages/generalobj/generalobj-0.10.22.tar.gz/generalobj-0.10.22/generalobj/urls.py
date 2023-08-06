from django.urls import path
from generalobj import views

urlpatterns = [
    path('download_excelsheet', views.download_excelsheet, \
            name='download_excelsheet'),
    path('set_gostatus', views.set_gostatus, name='set_gostatus'),
]