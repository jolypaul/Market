from django.db import models

# Creation d'une classe pour une livraison
class Livraison(models.Model):
    livreur = models.ForeignKey('Authentification.Livreur', on_delete=models.CASCADE)
    client = models.ForeignKey('Authentification.Client', on_delete=models.CASCADE)
    adresse_livraison = models.CharField(max_length=255)
    date_livraison = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=50, choices=[('en_cours', 'En Cours'), ('livree', 'Livrée'), ('annulee', 'Annulée')], default='en_cours')
    

    def __str__(self):
        return f"Livraison {self.id} - {self.statut}"

    class Meta:
        verbose_name = 'Livraison'
        verbose_name_plural = 'Livraisons'
        ordering = ['date_livraison']
        
# Creation d'une classe pour les détails de livraison
class DetailLivraison(models.Model):
    livraison = models.ForeignKey(Livraison, related_name='details', on_delete=models.CASCADE)
    produit = models.ForeignKey('GestionProduits.Produit', on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)
    prix_de_livraison = models.DecimalField(max_digits=10, decimal_places=0)

    def __str__(self):
        return f"Detail Livraison {self.id} - {self.produit.nom}"

    class Meta:
        verbose_name = 'Détail Livraison'
        verbose_name_plural = 'Détails Livraisons'
        ordering = ['livraison__date_livraison']

# Creation d'une classe pour les évaluations de livraison
class EvaluationLivraison(models.Model):
    livraison = models.ForeignKey(Livraison, on_delete=models.CASCADE)
    client = models.ForeignKey('Authentification.Client', on_delete=models.CASCADE)
    note = models.PositiveIntegerField(default=0)
    commentaire = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Evaluation Livraison {self.id} - Note: {self.note}"

    class Meta:
        verbose_name = 'Évaluation Livraison'
        verbose_name_plural = 'Évaluations Livraisons'
        ordering = ['livraison__date_livraison']

# Creation d'une classe pour les notifications de livraison
