from django.db import models
from Market.Authentification.models import Utilisateur
from Market.GestionProduits.models import Produit

class Commande(models.Model):
    client = models.ForeignKey('Authentification.Client', on_delete=models.CASCADE)
    date_commande = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=50, choices=[('en_attente', 'En attente'), ('en_cours', 'En cours'), ('livree', 'Livrée')], default='en_attente')
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Commande {self.id} - {self.client.utilisateur.nom}"

    class Meta:
        verbose_name = 'Commande'
        verbose_name_plural = 'Commandes'
        ordering = ['-date_commande']
