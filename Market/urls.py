from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path,include
from .views import login,register,Dashboard_client,tout_les_produits,dashboard_client_avis,Dashboard_vendeur,produit,categorie,Dashboard_Livreur,form_modifier_produit,page_produits,appeler_page_favorie,call_profil,call_form_update_profil

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('Authentification.urls')),
    path('',include('Publication.urls')),
    path('produit/',include('GestionProduits.urls')),
    path('',include('Favoris.urls')),
    path('commande/', include('Commande.urls')),
    path('panier/', include('Panier.urls')),
    path('paiement/', include('Paiement.urls')),
    path('',login, name='login'),
    path('register/',register,name='register'),
    path('Dashboard_client/',Dashboard_client,name='Dashboard_client'),
    path('dashboard_client_avis/',dashboard_client_avis,name='dashboard_client_avis'),
    path('Dashboard_vendeur/',Dashboard_vendeur,name='Dashboard_vendeur'),
    path('Dashboard_Livreur/',Dashboard_Livreur,name='Dashboard_Livreur'),
    path('tout_les_produits/',tout_les_produits,name='tout_les_produits'),
    path('call_profil/',call_profil,name='call_profil'),
    path('produit/',produit,name='produit'),
    path('appeler_page_favorie/',appeler_page_favorie,name='appeler_page_favorie'),
    path('categorie/',categorie,name='categorie'),
    path('form_modifier_produit/<int:id>',form_modifier_produit,name='form_modifier_produit'),
    path('page_produits/',page_produits,name='page_produits'),
    path('call_form_update_profil/',call_form_update_profil,name='call_form_update_profil'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)