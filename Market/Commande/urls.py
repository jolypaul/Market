#url de l'application commande
from django.urls import path
from . import views

urlpatterns = [
    # URL pour passer une commande
    path('commander/', views.creer_commande, name='passer_commande'),
    
    #details d'une commande
    path('commande/<int:commande_id>/', views.details_commande, name='detail_commande'),
    
    # URL pour afficher l'historique des commandes d'un client
    path('historique_commandes/', views.historique_commandes, name='historique_commandes'),
    
    #lister les commandes (admin)
    path('commandes/', views.liste_commandes, name='liste_commandes'),
    
    #annuler une commande
    path('commande/<int:commande_id>/annuler/', views.annuler_commande, name='annuler_commande'),
    
    #sivre une commande
    path('commande/<int:commande_id>/suivre/', views.suivre_commande, name='suivre_commande'),
    
    #evaluer une commande
    path('commande/<int:commande_id>/evaluer/', views.evaluer_commande, name='evaluer_commande'),
    
    
]   