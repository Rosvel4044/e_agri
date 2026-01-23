
from django.urls import path
from .views import index



urlpatterns = [
    path('base.html',index,name="e_agri-index"),
]