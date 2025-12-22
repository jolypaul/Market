from django.urls import path
from . import views

urlpatterns = [
    path('paiement/commande/<int:commande_id>/', views.payer_commande, name='payer_commande'),
    path('paiements/', views.historique_paiements, name='historique_paiements'),
    path('paiement/<int:paiement_id>/', views.detail_paiement, name='detail_paiement'),
]
