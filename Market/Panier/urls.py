from django.urls import path
from . import views

urlpatterns = [
    path('panier/', views.afficher_panier, name='afficher_panier'),
    path('panier/ajouter/<int:produit_id>/', views.ajouter_au_panier, name='ajouter_au_panier'),
    path('panier/supprimer/<int:produit_id>/', views.supprimer_du_panier, name='supprimer_du_panier'),
    path('panier/quantite/<int:produit_id>/', views.mettre_a_jour_quantite, name='mettre_a_jour_quantite'),
    path('panier/vider/', views.vider_panier, name='vider_panier'),
]
