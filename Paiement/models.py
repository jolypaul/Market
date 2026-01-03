from django.db import models
import uuid


class Paiement(models.Model):
    STATUT_CHOICES = [
        ('en_cours', 'En Cours'),
        ('confirme', 'Confirmé'),
        ('effectue', 'Effectué'),
        ('echec', 'Échoué'),
        ('annule', 'Annulé'),
        ('rembourse', 'Remboursé'),
    ]
    
    TYPE_PAIEMENT_CHOICES = [
        ('carte', 'Carte Bancaire'),
        ('paypal', 'PayPal'),
        ('virement', 'Virement'),
        ('autre', 'Autre'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference = models.CharField(max_length=100, unique=True, db_index=True)
    client = models.ForeignKey('Authentification.Client', on_delete=models.CASCADE, related_name='paiements')
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    devise = models.CharField(max_length=3, default='EUR')
    date_paiement = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    statut = models.CharField(max_length=50, choices=STATUT_CHOICES, default='en_cours')
    type_paiement = models.CharField(max_length=50, choices=TYPE_PAIEMENT_CHOICES, default='carte')
    commande = models.OneToOneField('Commande.Commande', on_delete=models.CASCADE, related_name='paiement', null=False, blank=False)
    
    # Intégration Stripe
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    stripe_charge_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Intégration PayPal
    paypal_transaction_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    
    description = models.TextField(blank=True, null=True)
    message_erreur = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Paiement'
        verbose_name_plural = 'Paiements'
        ordering = ['-date_paiement']
        unique_together = [['commande']]  # Une seule paiement par commande
    
    def __str__(self):
        return f"Paiement {self.reference} - {self.client.utilisateur.nom} ({self.statut})"
    
    def marquer_effectue(self):
        """Marque le paiement comme effectué"""
        self.statut = 'effectue'
        self.save()
        
        # Mettre à jour le statut de la commande
        self.commande.statut = 'confirmee'
        self.commande.save()
    
    def marquer_echoue(self, message_erreur=None):
        """Marque le paiement comme échoué"""
        self.statut = 'echec'
        if message_erreur:
            self.message_erreur = message_erreur
        self.save()
    
    def rembourser(self):
        """Marque le paiement comme remboursé"""
        self.statut = 'rembourse'
        self.save()


class HistoriquePaiement(models.Model):
    """Historique des tentatives de paiement"""
    paiement = models.ForeignKey(Paiement, on_delete=models.CASCADE, related_name='historique')
    date = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=100)  # 'tentative', 'succes', 'echec', 'remboursement'
    statut_avant = models.CharField(max_length=50)
    statut_apres = models.CharField(max_length=50)
    message = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Historique Paiement'
        verbose_name_plural = 'Historiques Paiements'
        ordering = ['-date']
    
    def __str__(self):
        return f"Historique {self.paiement.reference} - {self.action} - {self.date}"



