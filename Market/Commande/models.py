from django.db import models


class Commande(models.Model):
    client = models.ForeignKey('Authentification.Client', on_delete=models.CASCADE)
    date_commande = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(
        max_length=50,
        choices=[
            ('en_attente', 'En attente'),
            ('en_cours', 'En cours'),
            ('livree', 'Livrée'),
            ('annulee', 'Annulée'),
        ],
        default='en_attente',
    )
    produits = models.ManyToManyField('GestionProduits.Produit', through='CommandeItem', related_name='commandes')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.PositiveSmallIntegerField(null=True, blank=True)
    commentaire = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Commande {self.id} - {self.client.utilisateur.nom}"

    class Meta:
        verbose_name = 'Commande'
        verbose_name_plural = 'Commandes'
        ordering = ['-date_commande']


class CommandeItem(models.Model):
    commande = models.ForeignKey('Commande', on_delete=models.CASCADE, related_name='items')
    produit = models.ForeignKey('GestionProduits.Produit', on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = 'Ligne de commande'
        verbose_name_plural = 'Lignes de commande'
        ordering = ['-commande__date_commande']
