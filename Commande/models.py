from django.db import models
from Authentification.models import Utilisateur, Client
from GestionProduits.models import Produit


class Commande(models.Model):
    STATUS_CHOICES = [
        ('en_attente', 'En attente de paiement'),
        ('confirmee', 'Confirmée'),
        ('en_cours', 'En cours de traitement'),
        ('preparee', 'Préparée'),
        ('expediee', 'Expédiée'),
        ('livree', 'Livrée'),
        ('annulee', 'Annulée'),
        ('remboursee', 'Remboursée'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='commandes')
    date_commande = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    statut = models.CharField(max_length=50, choices=STATUS_CHOICES, default='en_attente')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    adresse_livraison = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Commande {self.id} - {self.client.utilisateur.nom}"
    
    def get_articles(self):
        """Retourne tous les articles de la commande"""
        return self.articles.all()
    
    def get_total_articles(self):
        """Retourne le nombre total d'articles"""
        return sum(article.quantite for article in self.articles.all())

    class Meta:
        verbose_name = 'Commande'
        verbose_name_plural = 'Commandes'
        ordering = ['-date_commande']


class ArticleCommande(models.Model):
    """Modèle pour stocker les articles d'une commande"""
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='articles')
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT)  # PROTECT pour ne pas supprimer si lié à une commande
    quantite = models.PositiveIntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)  # Prix au moment de la commande
    sous_total = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantite}x {self.produit.nom} - Commande {self.commande.id}"
    
    def save(self, *args, **kwargs):
        """Calcul automatique du sous-total"""
        self.sous_total = self.prix_unitaire * self.quantite
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Article Commande'
        verbose_name_plural = 'Articles Commande'
