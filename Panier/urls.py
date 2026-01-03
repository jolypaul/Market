from django.urls import path
from .views import (
    vue_panier, 
    ajouter_panier, 
    retirer_panier,
    modifier_quantite_panier,
    vider_panier
    , sync_panier_from_localstorage
)

urlpatterns = [
    path('panier/', vue_panier, name='vue_panier'),
    path('panier/ajouter/<int:produit_id>/', ajouter_panier, name='ajouter_panier'),
    path('panier/retirer/<int:article_id>/', retirer_panier, name='retirer_panier'),
    path('panier/modifier/<int:article_id>/', modifier_quantite_panier, name='modifier_quantite_panier'),
    path('panier/vider/', vider_panier, name='vider_panier'),
    path('panier/sync/', sync_panier_from_localstorage, name='sync_panier'),
]
