from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from GestionProduits.models import Produit


def afficher_panier(request):
    panier = request.session.get('panier', {})
    produits = []
    total = 0
    
    for produit_id, quantite in panier.items():
        try:
            produit = Produit.objects.get(id=int(produit_id))
            produits.append({'produit': produit, 'quantite': quantite, 'sous_total': produit.prix * quantite})
            total += produit.prix * quantite
        except Produit.DoesNotExist:
            del panier[produit_id]
    
    request.session['panier'] = panier
    return render(request, 'afficher_panier.html', {'produits': produits, 'total': total})


def ajouter_au_panier(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)
    panier = request.session.get('panier', {})
    
    quantite = int(request.POST.get('quantite', 1))
    panier[str(produit_id)] = panier.get(str(produit_id), 0) + quantite
    
    request.session['panier'] = panier
    messages.success(request, f"{produit.nom} ajouté au panier.")
    return redirect('afficher_panier')


def supprimer_du_panier(request, produit_id):
    panier = request.session.get('panier', {})
    
    if str(produit_id) in panier:
        del panier[str(produit_id)]
        request.session['panier'] = panier
        messages.success(request, "Produit supprimé du panier.")
    
    return redirect('afficher_panier')


def mettre_a_jour_quantite(request, produit_id):
    panier = request.session.get('panier', {})
    quantite = int(request.POST.get('quantite', 0))
    
    if str(produit_id) in panier:
        if quantite > 0:
            panier[str(produit_id)] = quantite
        else:
            del panier[str(produit_id)]
        request.session['panier'] = panier
        messages.success(request, "Quantité mise à jour.")
    
    return redirect('afficher_panier')


def vider_panier(request):
    request.session['panier'] = {}
    messages.success(request, "Panier vidé.")
    return redirect('afficher_panier')
