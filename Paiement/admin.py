from django.contrib import admin
from .models import Paiement, HistoriquePaiement


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ('reference', 'client', 'montant', 'devise', 'statut', 'type_paiement', 'date_paiement')
    search_fields = ('reference', 'client__utilisateur__nom', 'stripe_payment_intent_id')
    list_filter = ('statut', 'type_paiement', 'date_paiement')
    readonly_fields = ('id', 'date_paiement', 'date_modification', 'get_historique')
    
    fieldsets = (
        ('Informations Paiement', {
            'fields': ('id', 'reference', 'montant', 'devise', 'type_paiement', 'statut')
        }),
        ('Client et Commande', {
            'fields': ('client', 'commande')
        }),
        ('Intégration Stripe', {
            'fields': ('stripe_payment_intent_id', 'stripe_charge_id'),
            'classes': ('collapse',)
        }),
        ('Intégration PayPal', {
            'fields': ('paypal_transaction_id',),
            'classes': ('collapse',)
        }),
        ('Messages Erreur', {
            'fields': ('message_erreur',),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('date_paiement', 'date_modification'),
            'classes': ('collapse',)
        }),
        ('Historique', {
            'fields': ('get_historique',),
            'classes': ('collapse',)
        })
    )
    
    def get_historique(self, obj):
        historique = obj.historique.all().order_by('-date')
        if not historique:
            return "Aucun historique"
        
        html = '<table style="width:100%; border-collapse: collapse;">'
        html += '<tr style="background:#f0f0f0;"><th style="border:1px solid #ddd; padding:8px;">Date</th><th style="border:1px solid #ddd; padding:8px;">Action</th><th style="border:1px solid #ddd; padding:8px;">Statut</th><th style="border:1px solid #ddd; padding:8px;">Message</th></tr>'
        
        for h in historique:
            html += f'<tr>'
            html += f'<td style="border:1px solid #ddd; padding:8px;">{h.date.strftime("%d/%m/%Y %H:%M")}</td>'
            html += f'<td style="border:1px solid #ddd; padding:8px;">{h.action}</td>'
            html += f'<td style="border:1px solid #ddd; padding:8px;">{h.statut_avant} → {h.statut_apres}</td>'
            html += f'<td style="border:1px solid #ddd; padding:8px;">{h.message or "-"}</td>'
            html += f'</tr>'
        
        html += '</table>'
        from django.utils.html import format_html
        return format_html(html)
    get_historique.short_description = 'Historique'


@admin.register(HistoriquePaiement)
class HistoriquePaiementAdmin(admin.ModelAdmin):
    list_display = ('paiement', 'date', 'action', 'statut_avant', 'statut_apres')
    search_fields = ('paiement__reference', 'message')
    list_filter = ('action', 'date')
    readonly_fields = ('date',)
    
    def has_add_permission(self, request):
        return False  # Historique créé automatiquement
    
    def has_delete_permission(self, request, obj=None):
        return False  # Ne pas supprimer l'historique
