"""
Script pour créer des données de test
Lancez via: python manage.py shell < create_test_data.py
"""

from Authentification.models import Utilisateur, Commercant, Client, Livreur
from GestionProduits.models import Categorie, Produit
from django.utils import timezone

# Créer l'utilisateur admin
print("Création de l'utilisateur admin...")
admin_user, created = Utilisateur.objects.get_or_create(
    email='admin@market.com',
    defaults={
        'nom': 'Admin',
        'prenom': 'Test',
        'telephone': '0123456789',
        'adresse': '123 Rue Admin',
        'role': 'admin',
        'is_staff': True,
        'is_superuser': True,
    }
)
if created:
    admin_user.set_password('admin123')
    admin_user.save()
    print(f"✓ Admin créé: {admin_user.email}")
else:
    print(f"✓ Admin existant: {admin_user.email}")

# Créer un commercant
print("\nCréation du commerçant...")
commercant_user, created = Utilisateur.objects.get_or_create(
    email='commercant@market.com',
    defaults={
        'nom': 'Dupont',
        'prenom': 'Jean',
        'telephone': '0612345678',
        'adresse': '456 Rue Commerce',
        'role': 'commercant',
    }
)
if created:
    commercant_user.set_password('pass123')
    commercant_user.save()
    print(f"✓ Commerçant créé: {commercant_user.email}")
else:
    print(f"✓ Commerçant existant: {commercant_user.email}")

# Lier à Commercant
commercant, created = Commercant.objects.get_or_create(
    Utilisateur_ptr_id=commercant_user.id,
    defaults={
        'nom_magasin': 'Magasin Dupont',
        'logo': '',
    }
)
if created:
    print(f"✓ Profil Commercant créé")
else:
    print(f"✓ Profil Commercant existant")

# Créer un client
print("\nCréation du client...")
client_user, created = Utilisateur.objects.get_or_create(
    email='client@market.com',
    defaults={
        'nom': 'Martin',
        'prenom': 'Marie',
        'telephone': '0687654321',
        'adresse': '789 Rue Client',
        'role': 'client',
    }
)
if created:
    client_user.set_password('pass123')
    client_user.save()
    print(f"✓ Client créé: {client_user.email}")
else:
    print(f"✓ Client existant: {client_user.email}")

# Lier à Client
client, created = Client.objects.get_or_create(
    Utilisateur_ptr_id=client_user.id,
    defaults={
        'historique_achat': '',
    }
)
if created:
    print(f"✓ Profil Client créé")
else:
    print(f"✓ Profil Client existant")

# Créer un livreur
print("\nCréation du livreur...")
livreur_user, created = Utilisateur.objects.get_or_create(
    email='livreur@market.com',
    defaults={
        'nom': 'Bernard',
        'prenom': 'Pierre',
        'telephone': '0654321098',
        'adresse': '321 Rue Livraison',
        'role': 'livreur',
    }
)
if created:
    livreur_user.set_password('pass123')
    livreur_user.save()
    print(f"✓ Livreur créé: {livreur_user.email}")
else:
    print(f"✓ Livreur existant: {livreur_user.email}")

# Lier à Livreur
livreur, created = Livreur.objects.get_or_create(
    Utilisateur_ptr_id=livreur_user.id,
    defaults={
        'moyen_livraison': 'Voiture',
        'zone_livraison': 'Paris',
    }
)
if created:
    print(f"✓ Profil Livreur créé")
else:
    print(f"✓ Profil Livreur existant")

# Créer des catégories
print("\nCréation des catégories...")
categories_data = [
    {'nom': 'Électronique', 'description': 'Produits électroniques'},
    {'nom': 'Vêtements', 'description': 'Vêtements et mode'},
    {'nom': 'Livres', 'description': 'Livres et littérature'},
    {'nom': 'Alimentaire', 'description': 'Produits alimentaires'},
]

categories = []
for cat_data in categories_data:
    cat, created = Categorie.objects.get_or_create(
        nom=cat_data['nom'],
        defaults={'description': cat_data['description']}
    )
    categories.append(cat)
    if created:
        print(f"✓ Catégorie créée: {cat.nom}")
    else:
        print(f"✓ Catégorie existante: {cat.nom}")

# Créer des produits
print("\nCréation des produits...")
produits_data = [
    {
        'nom': 'Laptop Dell XPS 13',
        'description': 'Ordinateur portable haute performance',
        'prix': 1299.99,
        'stock': 10,
        'categorie': categories[0],  # Électronique
    },
    {
        'nom': 'T-shirt Coton Premium',
        'description': 'T-shirt confortable en coton 100%',
        'prix': 29.99,
        'stock': 50,
        'categorie': categories[1],  # Vêtements
    },
    {
        'nom': 'Clean Code',
        'description': 'Un manuel pour mieux coder - Robert C. Martin',
        'prix': 45.00,
        'stock': 20,
        'categorie': categories[2],  # Livres
    },
    {
        'nom': 'Café Premium 1kg',
        'description': 'Café moulu de haute qualité',
        'prix': 15.99,
        'stock': 100,
        'categorie': categories[3],  # Alimentaire
    },
    {
        'nom': 'Casque Bluetooth Sony',
        'description': 'Casque sans fil avec réduction de bruit',
        'prix': 199.99,
        'stock': 15,
        'categorie': categories[0],  # Électronique
    },
    {
        'nom': 'Jeans Levi\'s 501',
        'description': 'Jean classique intemporel',
        'prix': 89.99,
        'stock': 30,
        'categorie': categories[1],  # Vêtements
    },
]

for prod_data in produits_data:
    prod, created = Produit.objects.get_or_create(
        nom=prod_data['nom'],
        defaults={
            'description': prod_data['description'],
            'prix': prod_data['prix'],
            'stock': prod_data['stock'],
            'categorie': prod_data['categorie'],
            'Commercant': commercant,
            'date_creation': timezone.now(),
        }
    )
    if created:
        print(f"✓ Produit créé: {prod.nom}")
    else:
        print(f"✓ Produit existant: {prod.nom}")

print("\n" + "="*50)
print("✓ Données de test créées avec succès!")
print("="*50)
print("\nComptes de test:")
print("  Admin:       admin@market.com / admin123")
print("  Commerçant:  commercant@market.com / pass123")
print("  Client:      client@market.com / pass123")
print("  Livreur:     livreur@market.com / pass123")
print("\nAccédez à l'admin: http://127.0.0.1:8000/admin/")
