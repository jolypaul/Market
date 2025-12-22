from django.urls import path
from .views import (
	categorie_Save,
	page_categories,
	crate_produit,
	liste_produits,
	detail_produit,
	modifierProduit,
	supprimer_produit,
	modifier_categorie,
	supprimer_categorie,
	liste_categories,
)

urlpatterns = [
	# produit list /produit/
	path('', liste_produits, name='liste_produits'),
	# create produit
	path('ajouter/', crate_produit, name='crate_produit'),
	# detail /produit/<id>/
	path('<int:produit_id>/', detail_produit, name='detail_produit'),
	# modify /produit/<id>/modifier/
	path('<int:produit_id>/modifier/', modifierProduit, name='modifierProduit'),
	# delete
	path('<int:produit_id>/supprimer/', supprimer_produit, name='supprimer_produit'),

	# categories
	path('categorie/ajouter/', categorie_Save, name='categorie_Save'),
	path('categorie/<int:cat_id>/supprimer/', supprimer_categorie, name='supprimer_categorie'),
	path('categorie/<int:categories_id>/modifier/', modifier_categorie, name='modifier_categorie'),
	path('categories/', liste_categories, name='liste_categories'),
	path('categorie/<int:cat_id>/', page_categories, name='page_categories'),
]
