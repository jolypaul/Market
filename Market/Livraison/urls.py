#Les routes de l'application livraison

from django.urls import path
from . import views

urlpatterns = [
    path('livraisons/', views.afficher_livraisons, name='afficher_livraisons'),
    path('livraison/<int:livraison_id>/suivre/', views.suivre_livraison, name='suivre_livraison'),
    path('livraison/<int:livraison_id>/evaluer/', views.evaluer_livraison, name='evaluer_livraison'),
    path('livraison/<int:livraison_id>/accepter/', views.accepter_livraison, name='accepter_livraison'),
]