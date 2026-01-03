from django.db import models
from Authentification.models import Client
from GestionProduits.models import Produit


class Panier(models.Model):
    """Modèle pour gérer le panier de chaque client"""
    client = models.OneToOneField(Client, on_delete=models.CASCADE, related_name='panier')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Panier de {self.client.utilisateur.nom}"
    
    def get_total(self):
        """Calcul du total du panier"""
        return sum(article.get_subtotal() for article in self.articles.all())
    
    def get_total_items(self):
        """Nombre total d'articles dans le panier"""
        return sum(article.quantite for article in self.articles.all())
    
    class Meta:
        verbose_name = 'Panier'
        verbose_name_plural = 'Paniers'


class ArticlePanier(models.Model):
    """Modèle pour les articles dans le panier"""
    panier = models.ForeignKey(Panier, on_delete=models.CASCADE, related_name='articles')
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)  # Prix au moment de l'ajout
    date_ajout = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.quantite}x {self.produit.nom}"
    
    def get_subtotal(self):
        """Calcul du sous-total pour cet article"""
        return self.prix_unitaire * self.quantite
    
    class Meta:
        verbose_name = 'Article Panier'
        verbose_name_plural = 'Articles Panier'
        ordering = ['-date_ajout']
