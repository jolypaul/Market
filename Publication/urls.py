from django.urls import path
from .views import creer_avis,supprimer_avis_commercant,modifier_avis_commercant,creer_avis_commercant,creer_commentaire_commercant,modifier_commentaire_commercant,modifier_avis,supprimer_avis

urlpatterns = [
path('creer_avis',creer_avis,name='creer_avis'),
path('creer_avis_commercant',creer_avis_commercant,name='creer_avis_commercant'),
path('modifier_avis/<int:avis_id>',modifier_avis,name='modifier_avis'),
path('supprimer_avis_commercant/<int:avis_id>',supprimer_avis_commercant,name='supprimer_avis_commercant'),
path('modifier_avis_commercant/<int:avis_id>',modifier_avis_commercant,name='modifier_avis_commercant'),
path('supprimer_avis/<int:avis_id>',supprimer_avis,name='supprimer_avis'),
path('modifier_commentaire_commercant/<int:commentaire_id>',modifier_commentaire_commercant,name='modifier_commentaire_commercant'),
path('creer_commentaire_commercant',creer_commentaire_commercant,name='creer_commentaire_commercant'),
]


