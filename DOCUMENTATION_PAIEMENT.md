# 🛒 Système de Panier et Paiement - Marché Virtuel

## 📋 Documentation Complète

Ce document couvre l'implémentation complète du système de panier, commandes et paiement en ligne pour votre plateforme e-commerce Django.

---

## 🏗️ Architecture et Flux

### Flux d'Achat Complet

```
1. Client consulte les produits
   ↓
2. Ajoute un produit au panier
   ↓
3. Consulte son panier (voir articles, modifier quantités)
   ↓
4. Procède au checkout
   ↓
5. Choisit l'adresse de livraison
   ↓
6. Sélectionne le mode de paiement
   ↓
7. Effectue le paiement via Stripe
   ↓
8. Reçoit la confirmation
   ↓
9. Suit sa commande
```

---

## 📦 Modèles de Données

### 1. Modèle `Panier`

```python
class Panier(models.Model):
    client = OneToOneField(Client)
    date_creation = DateTimeField()
    date_modification = DateTimeField()
    
    # Méthodes utiles
    get_total()           # Retourne le total du panier
    get_total_items()     # Nombre d'articles
```

**Utilité**: Stocke les articles actuels du client avant la commande.

### 2. Modèle `ArticlePanier`

```python
class ArticlePanier(models.Model):
    panier = ForeignKey(Panier)
    produit = ForeignKey(Produit)
    quantite = PositiveIntegerField()
    prix_unitaire = DecimalField()  # Prix de référence
    date_ajout = DateTimeField()
    
    # Méthodes
    get_subtotal()  # quantite * prix_unitaire
```

**Utilité**: Représente chaque produit dans le panier.

### 3. Modèle `Commande` (Amélioré)

```python
class Commande(models.Model):
    client = ForeignKey(Client)
    date_commande = DateTimeField()
    statut = CharField()  # en_attente, confirmee, en_cours, livree, annulee
    total = DecimalField()
    adresse_livraison = TextField()
    notes = TextField()
    
    # Méthodes
    get_articles()        # Articles de la commande
    get_total_articles()  # Nombre total d'articles
```

**Statuts disponibles**:
- `en_attente` : En attente de paiement
- `confirmee` : Paiement confirmé
- `en_cours` : Préparation
- `preparee` : Prête à expédier
- `expediee` : En transit
- `livree` : Livrée
- `annulee` : Annulée
- `remboursee` : Remboursée

### 4. Modèle `ArticleCommande`

```python
class ArticleCommande(models.Model):
    commande = ForeignKey(Commande)
    produit = ForeignKey(Produit)
    quantite = PositiveIntegerField()
    prix_unitaire = DecimalField()  # Prix au moment de la commande
    sous_total = DecimalField()
```

**Utilité**: Archive des articles commandés (immutable, pour l'historique).

### 5. Modèle `Paiement` (Amélioré)

```python
class Paiement(models.Model):
    reference = CharField()              # Identifiant unique
    client = ForeignKey(Client)
    montant = DecimalField()
    devise = CharField()  # EUR, USD...
    commande = OneToOneField(Commande)
    statut = CharField()  # en_cours, confirme, effectue, echec, annule, rembourse
    type_paiement = CharField()  # carte, paypal, virement
    
    # Intégration Stripe
    stripe_payment_intent_id = CharField()
    stripe_charge_id = CharField()
    
    # Intégration PayPal
    paypal_transaction_id = CharField()
    
    message_erreur = TextField()
```

### 6. Modèle `HistoriquePaiement`

```python
class HistoriquePaiement(models.Model):
    paiement = ForeignKey(Paiement)
    date = DateTimeField()
    action = CharField()  # tentative, succes, echec, remboursement
    statut_avant = CharField()
    statut_apres = CharField()
    message = TextField()
```

**Utilité**: Traçabilité complète des tentatives et modifications de paiement.

---

## 🔌 Endpoints API et Vues

### Panier

#### `GET /panier/panier/`
Affiche le panier du client connecté.

**Paramètres**: Aucun
**Retour**: Template `panier.html`
**Authentification**: Client requis

```html
{% include 'panier.html' %}
```

#### `POST /panier/panier/ajouter/<int:produit_id>/`
Ajoute un produit au panier.

**Paramètres POST**:
- `quantite` (int, optionnel, défaut 1)

**Retour**: Redirection ou JSON si AJAX
```json
{
    "success": true,
    "message": "Produit ajouté",
    "total_articles": 5,
    "total": "150.50"
}
```

#### `GET /panier/panier/retirer/<int:article_id>/`
Retire un article du panier.

**Retour**: Redirection + message ou JSON

#### `POST /panier/panier/modifier/<int:article_id>/`
Modifie la quantité d'un article.

**Paramètres**:
- `quantite` (int)

**Retour JSON**:
```json
{
    "success": true,
    "subtotal": "50.00",
    "total": "150.50",
    "total_articles": 5
}
```

#### `POST /panier/panier/vider/`
Vide complètement le panier.

**Retour**: Message de confirmation

---

### Commandes

#### `GET /commande/creer/`
Affiche la page de finalisation de la commande (checkout).

**Retour**: Template `checkout.html`

#### `POST /commande/creer/`
Crée la commande depuis le panier.

**Paramètres POST**:
- `adresse_livraison` (string)
- `notes` (string, optionnel)
- `type_paiement` (string, défaut 'carte')

**Actions effectuées**:
1. Vérifie le panier (non vide)
2. Vérifie le stock
3. Crée la commande
4. Copie les articles du panier
5. Réduit le stock
6. Vide le panier
7. Crée un paiement
8. Redirige vers le paiement

#### `GET /commande/liste/`
Liste toutes les commandes du client.

**Retour**: Template `liste_commandes.html`

#### `GET /commande/detail/<int:commande_id>/`
Détails d'une commande.

**Retour**: Template `detail_commande.html`

#### `GET /commande/annuler/<int:commande_id>/`
Annule une commande.

**Conditions**:
- Statut doit être `en_attente` ou `confirmee`
- Rembourse le stock
- Annule le paiement

---

## 💳 Système de Paiement Stripe

### Configuration Requise

1. **Clés Stripe**:
   - `STRIPE_PUBLIC_KEY`: Clé publique (visible au client)
   - `STRIPE_SECRET_KEY`: Clé secrète (serveur uniquement)
   - `STRIPE_WEBHOOK_SECRET`: Secret pour valider les webhooks

2. **Installation**:
```bash
pip install stripe
```

3. **Configuration dans `settings.py`**:
```python
STRIPE_PUBLIC_KEY = 'pk_test_...'
STRIPE_SECRET_KEY = 'sk_test_...'
STRIPE_WEBHOOK_SECRET = 'whsec_...'
```

### Endpoints de Paiement

#### `GET /paiement/checkout/<uuid:paiement_id>/`
Page de paiement avec formulaire Stripe Elements.

**Workflow**:
1. Récupère le paiement
2. Crée un PaymentIntent si absent
3. Affiche le formulaire Stripe
4. Retourne le `client_secret`

**Retour**: Template `paiement_checkout.html`

#### `POST /paiement/confirmer/<uuid:paiement_id>/`
Confirme le paiement avec la carte.

**Paramètres**:
- `payment_method_id` (string, généré par Stripe.js)

**Retour JSON**:
```json
{
    "success": true,
    "client_secret": "pi_1234...",
    "status": "succeeded"
}
```

#### `POST /paiement/webhook/stripe/`
Webhook Stripe (pas d'authentification).

**Événements traités**:
- `payment_intent.succeeded`: Paiement réussi
- `payment_intent.payment_failed`: Paiement échoué
- `charge.refunded`: Remboursement

#### `GET /paiement/succes/?paiement_id=...`
Page de confirmation de paiement.

**Retour**: Template `paiement_succes.html`

#### `GET /paiement/erreur/?paiement_id=...`
Page d'erreur de paiement.

**Retour**: Template `paiement_erreur.html`

---

## 🎨 Templates Créés

### 1. `panier.html`
- Affiche les articles du panier
- Permet de modifier les quantités
- Affiche le total
- Boutons d'action (paiement, continuer, vider)

### 2. `checkout.html`
- Résumé de la commande
- Formulaire d'adresse de livraison
- Sélection du mode de paiement
- Conditions d'utilisation

### 3. `paiement_checkout.html`
- Formulaire de paiement Stripe
- Résumé du montant
- Traitement sécurisé avec Stripe.js

### 4. `paiement_succes.html`
- Confirmation de paiement
- Détails de la commande
- Prochaines étapes
- Informations de suivi

### 5. `paiement_erreur.html`
- Message d'erreur
- Raison de l'échec
- Conseils pour résoudre
- Support client

### 6. `liste_commandes.html`
- Liste des commandes du client
- Statut de chaque commande
- Actions possibles

### 7. `detail_commande.html`
- Détails complets de la commande
- Articles commandés
- Timeline du statut
- Actions disponibles

---

## 🔒 Sécurité

### Protection CSRF
Tous les formulaires incluent `{% csrf_token %}`.

### Authentification
- Tous les endpoints de panier/commande vérifient `request.session['role'] == 'client'`
- Les clients ne peuvent voir que leurs propres commandes

### Paiement
- **Stripe.js**: Gère les cartes en client-side (aucune donnée sensible côté serveur)
- **PaymentIntent**: Stripe crée un intent pour chaque transaction
- **Webhooks signés**: Stripe signe les webhooks, vérification obligatoire
- **Montants**: Vérifiés côté serveur avant crédit

### Données Sensibles
- Clés Stripe en variable d'environnement (`settings.py` à ajouter à `.gitignore`)
- Pas de stockage de numéros de carte
- Logs sécurisés (IDs paiement, pas montants)

---

## 🔄 Flux de Paiement Détaillé

```
1. Client clique "Procéder au Paiement"
   ↓
2. Création Commande + Paiement (status: en_cours)
   ↓
3. PaymentIntent Stripe créé
   ↓
4. Page paiement affichée avec Stripe Elements
   ↓
5. Client saisit carte (côté client Stripe.js)
   ↓
6. Client clique "Payer"
   ↓
7. Payment Method créé (client-side)
   ↓
8. Envoi au serveur → confirmer PaymentIntent
   ↓
9. Stripe traite le paiement
   ↓
10. Webhook reçu (payment_intent.succeeded)
    ↓
11. Statut paiement = "effectue"
    ↓
12. Statut commande = "confirmee"
    ↓
13. Redirection page succès
    ↓
14. Notification client
```

---

## 🧪 Tests et Déploiement

### Clés de Test Stripe

Pour tester sans vraie carte:

```
Carte Visa: 4242 4242 4242 4242
Date: 12/25 (future)
CVC: 123
Zip: 12345
```

### Vérification Pré-Déploiement

1. ✅ Vérifier les clés Stripe en `.env` ou variables d'environnement
2. ✅ Tester le webhook Stripe (`ngrok` ou IP publique)
3. ✅ Vérifier les migrations (`python manage.py migrate`)
4. ✅ Tester le flux complet (panier → commande → paiement)
5. ✅ Vérifier les mails de confirmation

### Migration Vers Production

```bash
# 1. Créer migrations
python manage.py makemigrations

# 2. Appliquer migrations
python manage.py migrate

# 3. Collecter fichiers statiques
python manage.py collectstatic

# 4. Vérifier clés Stripe
# Mettre à jour STRIPE_PUBLIC_KEY, STRIPE_SECRET_KEY
# avec vos clés LIVE (pk_live_..., sk_live_...)

# 5. Configurer le webhook Stripe
# URL: https://votresite.com/paiement/webhook/stripe/
# Événements: payment_intent.succeeded, payment_intent.payment_failed, charge.refunded
```

---

## 📊 Améliorations Futures

1. **PayPal**: Intégration complète
2. **Autres modes de paiement**: Virement, crypto
3. **Notifications**: Emails/SMS à chaque étape
4. **Factures**: Génération PDF
5. **Retours/Remboursements**: Interface admin
6. **Analytics**: Tableau de bord ventes
7. **Recommandations**: IA pour produits similaires
8. **Reviews**: Permettre notes après livraison

---

## 🆘 Dépannage

### "AttributeError: object has no attribute 'get_total'"

**Cause**: `ArticlePanier` ne retourne pas le sous-total
**Solution**: Appeler `article.get_subtotal()` (pas `get_total()`)

### Paiement en boucle infinie

**Cause**: Webhook non configuré ou non signalé
**Solution**: Vérifier `STRIPE_WEBHOOK_SECRET` et URL du webhook

### Article en double dans le panier

**Cause**: Pas de vérification lors de l'ajout
**Solution**: Le code vérifie déjà, si ça arrive, vérifier la BD

### Commande crée mais paiement absent

**Cause**: Exception avant `Paiement.objects.create()`
**Solution**: Vérifier les logs, commande doit avoir `total` valide

---

## 📞 Support et Questions

Pour toute question sur cette implémentation:
1. Vérifiez la documentation Stripe officielle
2. Consultez les logs Django (`debug.log`)
3. Testez avec les cartes de test Stripe
4. Vérifiez les paramètres de configuration

---

**Version**: 1.0  
**Dernière mise à jour**: Janvier 2026  
**Statut**: Production-Ready ✅
