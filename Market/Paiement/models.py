from django.db import models

# creation d'une classe pour un paiement pour ceux qui veulent payer en ligne
class Paiement(models.Model):
    reference = models.CharField(max_length=100, unique=True)
    client = models.ForeignKey('Authentification.Client', on_delete=models.CASCADE)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_paiement = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=50, choices=[('en_cours', 'En Cours'), ('effectue', 'Effectué'), ('annule', 'Annulé')], default='en_cours')
    type_paiement = models.CharField(max_length=50, choices=[('carte', 'Carte'), ('paypal', 'PayPal'), ('virement', 'Virement')], default='carte')
    commande = models.ForeignKey('Commande.Commande', on_delete=models.CASCADE, null=False, blank=False)
    description = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"Paiement {self.reference} - {self.client.utilisateur.nom}"
    class Meta:
        verbose_name = 'Paiement'
        verbose_name_plural = 'Paiements'
        ordering = ['-date_paiement']


