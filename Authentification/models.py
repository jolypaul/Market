from django.db import models

class Utilisateur(models.Model):
    email = models.EmailField(unique=True)
    nom = models.CharField(max_length=150)
    image = models.ImageField(upload_to='utilisateurs/', blank=True, null=True)
    motDePasse = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
        ordering = ['nom']

#Creation d'une classe client
class Client(models.Model):
    utilisateur = models.OneToOneField(Utilisateur, on_delete=models.CASCADE)
    adresse = models.CharField(max_length=255, blank=False, null=False)
    telephone = models.CharField(max_length=15, blank=False, null=False)

    def __str__(self):
        return f"{self.utilisateur.nom} - {self.adresse if self.adresse else 'No Address'}"

    class Meta:
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'
        ordering = ['utilisateur__nom']
        
# Creation d'une classe administrateur
class Administrateur(models.Model):
    utilisateur = models.OneToOneField(Utilisateur, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=[('superadmin', 'Super Admin'), ('admin', 'Admin')], default='admin')

    def __str__(self):
        return f"{self.utilisateur.nom} - {self.role}"

    class Meta:
        verbose_name = 'Administrateur'
        verbose_name_plural = 'Administrateurs'
        ordering = ['utilisateur__nom']
        
    #creation d'une classe pour un commerçant
class Commercant(models.Model):
    utilisateur = models.OneToOneField(Utilisateur, on_delete=models.CASCADE)
    boutique_nom = models.CharField(max_length=100, blank=True, null=True)
    adresse_boutique = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.utilisateur.nom} - {self.boutique_nom if self.boutique_nom else 'No Shop Name'}"

    class Meta:
        verbose_name = 'Commercant'
        verbose_name_plural = 'Commercants'
        ordering = ['utilisateur__nom']
        
        #Creation d'une classe pour un livreur
class Livreur(models.Model):
    utilisateur = models.OneToOneField(Utilisateur, on_delete=models.CASCADE)
    zone_de_livraison = models.CharField(max_length=100, blank=False, null=False)
    telephone = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.utilisateur.nom} - {self.zone_de_livraison if self.zone_de_livraison else 'No Delivery Zone'}"

    class Meta:
        verbose_name = 'Livreur'
        verbose_name_plural = 'Livreurs'
        ordering = ['utilisateur__nom']

