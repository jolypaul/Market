from django.contrib import admin
from .models import Panier, ArticlePanier


@admin.register(Panier)
class PanierAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'date_creation', 'get_total', 'get_total_items')
    search_fields = ('client__utilisateur__nom', 'client__utilisateur__email')
    readonly_fields = ('date_creation', 'date_modification', 'get_total', 'get_total_items')
    list_filter = ('date_creation', 'date_modification')
    
    def get_total(self, obj):
        return f"{obj.get_total()} €"
    get_total.short_description = 'Total'
    
    def get_total_items(self, obj):
        return obj.get_total_items()
    get_total_items.short_description = 'Nombre d\'articles'


@admin.register(ArticlePanier)
class ArticlePanierAdmin(admin.ModelAdmin):
    list_display = ('id', 'produit', 'panier_client', 'quantite', 'prix_unitaire', 'get_subtotal', 'date_ajout')
    search_fields = ('produit__nom', 'panier__client__utilisateur__nom')
    readonly_fields = ('date_ajout', 'get_subtotal')
    list_filter = ('date_ajout', 'panier')
    
    def panier_client(self, obj):
        return obj.panier.client.utilisateur.nom
    panier_client.short_description = 'Client'
    
    def get_subtotal(self, obj):
        return f"{obj.get_subtotal()} €"
    get_subtotal.short_description = 'Sous-total'
