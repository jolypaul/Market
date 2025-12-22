from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .models import Commande, CommandeItem
from Authentification.models import Client
from GestionProduits.models import Produit
from django.contrib import messages


def creer_commande(request):
    client = get_object_or_404(Client, utilisateur=request.user)
    panier = request.session.get('panier', {})
    
    if not panier:
        messages.error(request, "Votre panier est vide.")
        return redirect('afficher_panier')
    
    with transaction.atomic():
        total_commande = 0
        # calculer total et créer la commande
        for pid, quantite in panier.items():
            produit = get_object_or_404(Produit, id=pid)
            total_commande += produit.prix * quantite

        commande = Commande.objects.create(client=client, total=total_commande)

        # créer les lignes de commande
        for produit_id, quantite in panier.items():
            produit = get_object_or_404(Produit, id=produit_id)
            CommandeItem.objects.create(
                commande=commande,
                produit=produit,
                quantite=quantite,
                prix_unitaire=produit.prix,
            )
        request.session['panier'] = {}  # Vider le panier après la commande
    
    messages.success(request, "Commande passée avec succès!")
    return redirect('details_commande', commande_id=commande.id)


def details_commande(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id, client__utilisateur=request.user)
    return render(request, 'details_commande.html', {'commande': commande})


def liste_commandes(request):
    client = get_object_or_404(Client, utilisateur=request.user)
    commandes = Commande.objects.filter(client=client).order_by('-date_commande')
    return render(request, 'liste_commandes.html', {'commandes': commandes})


def annuler_commande(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id, client__utilisateur=request.user)
    
    if commande.statut != 'en_attente':
        messages.error(request, "Vous ne pouvez pas annuler cette commande.")
        return redirect('details_commande', commande_id=commande.id)
    
    commande.statut = 'annulee'
    commande.save()
    messages.success(request, "Commande annulée avec succès.")
    return redirect('liste_commandes')

@login_required
def historique_commandes(request):
    client = get_object_or_404(Client, utilisateur=request.user)
    commandes = Commande.objects.filter(client=client).order_by('-date_commande')
    return render(request, 'historique_commandes.html', {'commandes': commandes})

@login_required
def suivre_commande(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id, client__utilisateur=request.user)
    return render(request, 'suivre_commande.html', {'commande': commande})

@login_required
def evaluer_commande(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id, client__utilisateur=request.user)
    
    if request.method == 'POST':
        note = int(request.POST.get('note'))
        commentaire = request.POST.get('commentaire')
        
        commande.note = note
        commande.commentaire = commentaire
        commande.save()
        
        messages.success(request, "Merci pour votre évaluation!")
        return redirect('details_commande', commande_id=commande.id)
    
    return render(request, 'evaluer_commande.html', {'commande': commande})
