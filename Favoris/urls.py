from django.contrib import admin
from django.urls import path
from .views import retirer_favori, ajouter_favori

urlpatterns = [
path('retirer_favori/<int:produit_id>',retirer_favori,name='retirer_favori'),
path('ajouter_favori/<int:produit_id>',ajouter_favori,name='ajouter_favori'),
]