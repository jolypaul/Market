from django.contrib import admin
from django.urls import path
from .views import connexion, inscription,reinitialiser_mdp,verifier_code,mot_de_passe_oublie,mwp

urlpatterns = [
path('connexion/',connexion,name='connexion'),
path('inscription/',inscription,name='inscription'),

    path('reinitialiser_mdp/', reinitialiser_mdp, name='reinitialiser_mdp'),
    path('verifier_code/', verifier_code, name='verifier_code'),
    path('mot_de_passe_oublie/', mot_de_passe_oublie, name='mot_de_passe_oublie'),
    path('mwp/', mwp, name='mwp'),
]