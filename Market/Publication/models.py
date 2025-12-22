#Il s'agot des modeles de l'application publication
from django.db import models

# Creation d'une classe pour une publication
class Publication(models.Model):
    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    date_publication = models.DateTimeField(auto_now_add=True)
    auteur = models.ForeignKey('Authentification.Commercant', on_delete=models.CASCADE)

    def __str__(self):
        return self.titre
    
    class Meta:
        verbose_name = 'Publication'
        verbose_name_plural = 'Publications'
        ordering = ['-date_publication']