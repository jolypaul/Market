#les routes de l'application publication
from django.urls import path
from . import views 


urlpatterns = [    # URL pour afficher les publications récentes
    path('publications/', views.afficher_publications, name='afficher_publications'),
    # URL pour modifier une publication spécifique
    path('publication/<int:publication_id>/modifier/', views.modifier_publication, name='modifier_publication'),
    # URL pour supprimer une publication spécifique
    path('publication/<int:publication_id>/supprimer/', views.supprimer_publication, name='supprimer_publication'),
    # URL pour ajouter une nouvelle publication
    path('publication/ajouter/', views.ajouter_publication, name='ajouter_publication'),
]