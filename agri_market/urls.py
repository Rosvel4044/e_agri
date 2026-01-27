
# agri_markets/urls.py

from django.urls import path
from . import views

app_name = 'agri_market'

urlpatterns = [
    path('inscription/', views.inscription, name='inscription'),
    path('connexion/',   views.connexion,   name='connexion'),
]
