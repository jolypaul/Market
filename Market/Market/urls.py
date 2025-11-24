from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path,include
from .views import login,register,produit,categorie,form_modifier_produit,page_produits,appeler_page_favorie

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/',include('Authentification.urls')),
    path('produit/',include('GestionProduits.urls')),
    path('',include('Favoris.urls')),
    path('',login, name='login'),
    path('register/',register,name='register'),
    path('produit/',produit,name='produit'),
    path('appeler_page_favorie/',appeler_page_favorie,name='appeler_page_favorie'),
    path('categorie/',categorie,name='categorie'),
    path('form_modifier_produit/<int:id>',form_modifier_produit,name='form_modifier_produit'),
    path('page_produits/',page_produits,name='page_produits'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)