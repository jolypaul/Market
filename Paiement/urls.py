from django.urls import path
from .views import (
    paiement_checkout,
    confirmer_paiement,
    paiement_succes,
    paiement_erreur,
    liste_paiements,
)

urlpatterns = [
    path('checkout/<uuid:paiement_id>/', paiement_checkout, name='paiement_checkout'),
    path('confirmer/<uuid:paiement_id>/', confirmer_paiement, name='confirmer_paiement'),
    path('succes/', paiement_succes, name='paiement_succes'),
    path('erreur/', paiement_erreur, name='paiement_erreur'),
    path('liste/', liste_paiements, name='liste_paiements'),
]
