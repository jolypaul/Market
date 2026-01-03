from django.db import models

class Favori(models.Model):
    client = models.ForeignKey('Authentification.Client', on_delete=models.CASCADE)
    produit = models.ForeignKey('GestionProduits.Produit', on_delete=models.CASCADE)
    
