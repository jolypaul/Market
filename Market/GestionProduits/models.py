from django.db import models

class Produit(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='', blank=True, null=True)
    prix = models.DecimalField(max_digits=10, decimal_places=0)
    quantite_en_stock = models.PositiveIntegerField(default=0)
    date_ajout = models.DateTimeField(auto_now_add=True)
    Commercant_id = models.ForeignKey('Authentification.Commercant', on_delete=models.CASCADE)
    categorie_id = models.ForeignKey('GestionProduits.Categorie', on_delete=models.CASCADE)

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = 'Produit'
        verbose_name_plural = 'Produits'
        ordering = ['nom']

#Creation d'une classe pour les catégories de produits
class Categorie(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'
        ordering = ['nom']