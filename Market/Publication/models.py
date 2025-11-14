from django.db import models

# creation d'une classe pour un avis ou commentaire
class Avis(models.Model):
    client = models.ForeignKey('Authentification.Client', on_delete=models.CASCADE)
    produit = models.ForeignKey('GestionProduits.Produit', on_delete=models.CASCADE)
    commentaire = models.TextField()
    note = models.PositiveIntegerField(default=0)
    date_creation = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Avis {self.id} - {self.produit.nom} - Note: {self.note}"
    class Meta:
        verbose_name = 'Avis'
        verbose_name_plural = 'Avis'
        ordering = ['-date_creation']
# Creation d'une classe pour un commentaire sur un commerçant
class CommentaireCommercant(models.Model):
    client = models.ForeignKey('Authentification.Client', on_delete=models.CASCADE)
    commercant = models.ForeignKey('Authentification.Commercant', on_delete=models.CASCADE)
    commentaire = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Commentaire {self.id} - {self.commercant.utilisateur.nom}"
    class Meta:
        verbose_name = 'Commentaire Commerçant'
        verbose_name_plural = 'Commentaires Commerçants'
        ordering = ['-date_creation']
        
# Creation d'une classe pour un avis sur un commerçant
class AvisCommercant(models.Model):
    client = models.ForeignKey('Authentification.Client', on_delete=models.CASCADE)
    commercant = models.ForeignKey('Authentification.Commercant', on_delete=models.CASCADE)
    note = models.PositiveIntegerField(default=0)
    commentaire = models.TextField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Avis Commerçant {self.id} - {self.commercant.utilisateur.nom} - Note: {self.note}"
    class Meta:
        verbose_name = 'Avis Commerçant'
        verbose_name_plural = 'Avis Commerçants'
        ordering = ['-date_creation']
        
# Creation d'une classe pour repondre à un commentaire sur un commerçant

class ReponseCommentaireCommercant(models.Model):
    commentaire = models.ForeignKey(CommentaireCommercant, related_name='reponses', on_delete=models.CASCADE)
    commercant = models.ForeignKey('Authentification.Commercant', on_delete=models.CASCADE)
    reponse = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Réponse {self.id} - {self.commercant.utilisateur.nom}"

    class Meta:
        verbose_name = 'Réponse Commentaire Commerçant'
        verbose_name_plural = 'Réponses Commentaires Commerçants'
        ordering = ['-date_creation']
