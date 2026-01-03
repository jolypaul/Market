from django.contrib import admin
from .models import Commande, ArticleCommande


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'date_commande', 'statut', 'total', 'get_articles_count')
    search_fields = ('client__utilisateur__nom', 'client__utilisateur__email', 'id')
    list_filter = ('statut', 'date_commande')
    readonly_fields = ('date_commande', 'date_modification', 'get_articles')
    
    fieldsets = (
        ('Informations Client', {
            'fields': ('client',)
        }),
        ('Détails de Commande', {
            'fields': ('date_commande', 'date_modification', 'statut', 'total')
        }),
        ('Livraison', {
            'fields': ('adresse_livraison', 'notes')
        }),
        ('Articles', {
            'fields': ('get_articles',),
            'classes': ('collapse',)
        })
    )
    
    def get_articles_count(self, obj):
        return obj.articles.count()
    get_articles_count.short_description = 'Nombre d\'articles'
    
    def get_articles(self, obj):
        articles = obj.articles.all()
        html = '<ul>'
        for article in articles:
            html += f'<li>{article.quantite}x {article.produit.nom} - {article.sous_total}€</li>'
        html += '</ul>'
        from django.utils.html import format_html
        return format_html(html)
    get_articles.short_description = 'Articles commandés'


@admin.register(ArticleCommande)
class ArticleCommandeAdmin(admin.ModelAdmin):
    list_display = ('id', 'commande', 'produit', 'quantite', 'prix_unitaire', 'sous_total')
    search_fields = ('produit__nom', 'commande__id')
    list_filter = ('commande__date_commande', 'commande__statut')
    readonly_fields = ('sous_total',)
    
    def has_add_permission(self, request):
        return False  # Empêcher l'ajout manuel (faire via Commande)
    
    def has_delete_permission(self, request, obj=None):
        return False  # Empêcher la suppression (maintenir l'historique)
