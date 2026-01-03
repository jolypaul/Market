from django.urls import path
from .views import (
    creer_commande,
    creer_commande_api,
    liste_commandes,
    detail_commande,
    annuler_commande
)

urlpatterns = [
    path('creer/', creer_commande, name='creer_commande'),
    path('liste/', liste_commandes, name='liste_commandes'),
    path('detail/<int:commande_id>/', detail_commande, name='detail_commande'),
    path('annuler/<int:commande_id>/', annuler_commande, name='annuler_commande'),
    path('creer_api/', creer_commande_api, name='creer_commande_api'),
]
