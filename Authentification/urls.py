from django.contrib import admin
from django.urls import path
from Authentification.views import connexion,inscription,reinitialiser_mdp,verifier_code,mot_de_passe_oublie,mwp,modifier_profil

urlpatterns = [
    path('connexion/',connexion,name='connexion'),
    path('inscription/',inscription,name='inscription'),
    path('modifier_profil/', modifier_profil, name='modifier_profil'),
    path('reinitialiser_mdp/', reinitialiser_mdp, name='reinitialiser_mdp'),
    path('verifier_code/', verifier_code, name='verifier_code'),
    path('mot_de_passe_oublie/', mot_de_passe_oublie, name='mot_de_passe_oublie'),
    path('mwp/', mwp, name='mwp'),
]