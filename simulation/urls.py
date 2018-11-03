from django.urls import path
from . import views

app_name = 'simulation'
urlpatterns = [
    path('generate/', views.generate, name='generate'),
    path('seal/', views.seal, name='seal'),
    path('transactions/', views.transactions, name='transactions'),
    path('blockchain/', views.blockchain, name='blockchain'),

    path('block/<str:block_hash>/', views.block_detail, name='block_detail'),

    path('verify/', views.verify, name='verify'),
    path('sync/', views.sync, name='sync'),
    path('sync_block/<int:block_id>/', views.sync_block, name='sync_block'),
]
