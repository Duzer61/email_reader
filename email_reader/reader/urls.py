from django.urls import path

from . import views

app_name = 'reader'

urlpatterns = [
    path('', views.index, name='index'),
]
