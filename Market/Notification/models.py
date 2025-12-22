from django.db import models

# creation d'une classe pour les notification
class Notification(models.Model):
    utilisateur = models.ForeignKey('Authentification.Utilisateur', on_delete=models.CASCADE)
    message = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
    lu = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification {self.id} - {self.utilisateur.nom}"

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-date_creation']
        
# Creation d'une classe pour les notifications de commande
class NotificationCommande(models.Model):
    commande = models.ForeignKey('Commande.Commande', on_delete=models.CASCADE)
    message = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
    lu = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification Commande {self.id} - {self.commande.client.utilisateur.nom}"

    class Meta:
        verbose_name = 'Notification Commande'
        verbose_name_plural = 'Notifications Commandes'
        ordering = ['-date_creation']
        
        
# Creation d'une classe pour les notifications de livraison
class NotificationLivraison(models.Model):
    livraison = models.ForeignKey('Livraison.Livraison', on_delete=models.CASCADE)
    message = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
    lu = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification Livraison {self.id} - {self.livraison.client.utilisateur.nom}"

    class Meta:
        verbose_name = 'Notification Livraison'
        verbose_name_plural = 'Notifications Livraisons'
        ordering = ['-date_creation']
        
    # Creation d'une classe pour les notifications de l'ajout produit par un admin ou un vendeur
class NotificationProduit(models.Model):
    produit = models.ForeignKey('GestionProduits.Produit', on_delete=models.CASCADE)
    message = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
    lu = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification Produit {self.id} - {self.produit.nom}"

    class Meta:
        verbose_name = 'Notification Produit'
        verbose_name_plural = 'Notifications Produits'
        ordering = ['-date_creation']
        
# Creation d'une classe pour les notifications de l'ajout catégorie

class NotificationCategorie(models.Model):
    categorie = models.ForeignKey('GestionProduits.Categorie', on_delete=models.CASCADE)
    message = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
    lu = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification Categorie {self.id} - {self.categorie.nom}"

    class Meta:
        verbose_name = 'Notification Categorie'
        verbose_name_plural = 'Notifications Categories'
        ordering = ['-date_creation']