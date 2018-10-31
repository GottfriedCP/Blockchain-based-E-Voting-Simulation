from django.urls import path
from . import views

app_name = 'ballot'
urlpatterns = [
    path('create/', views.create, name='create'),
    path('seal/', views.seal, name='seal'),
]
