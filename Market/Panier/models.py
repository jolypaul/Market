from django.db import models

# Creation d'une classe pour un panier d'achat
class Panier(models.Model):
    client = models.ForeignKey('Authentification.Client', on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)
    est_valide = models.BooleanField(default=False)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    