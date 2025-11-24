from django.urls import path
from .views import categorie_Save,page_categories,crate_produit,liste_produits,detail_produit,modifierProduit,supprimer_produit,modifier_categorie,supprimer_categorie,liste_categories

urlpatterns = [
path('categorie_Save/',categorie_Save,name="categorie_Save"),
path('crate_produit/',crate_produit,name="crate_produit"),
path('liste_produits/',liste_produits,name="liste_produits"),
path('detail_produit/<int:id>',detail_produit,name="detail_produit"),
path('liste_produits/',liste_produits,name="liste_produits"),
path('modifierProduit/<int:produit_id>/',modifierProduit,name="modifierProduit"),
path('supprimer_produit/<int:produit_id>',supprimer_produit,name="supprimer_produit"),
path('supprimer_categorie/<int:cat_id>',supprimer_categorie,name="supprimer_categorie"),
path('modifier_categorie/<int:categories_id>/', modifier_categorie, name="modifier_categorie"),
path('liste_categories/',liste_categories,name="liste_categories"),
path('page_categories/<int:cat_id>/',page_categories,name="page_categories"),
]
