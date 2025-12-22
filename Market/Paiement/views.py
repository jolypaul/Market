from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Paiement
from Commande.models import Commande
from Authentification.models import Client


@login_required
def payer_commande(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id, client__utilisateur=request.user)
    
    if request.method == 'POST':
        type_paiement = request.POST.get('type_paiement', 'carte')
        # Créer un paiement
        paiement = Paiement.objects.create(
            reference=f"PAY-{commande.id}-{commande.date_commande.timestamp()}",
            client=commande.client,
            montant=commande.total,
            type_paiement=type_paiement,
            commande=commande,
        )
        messages.success(request, "Paiement créé ! Statut : en cours.")
        return redirect('detail_paiement', paiement_id=paiement.id)
    
    return render(request, 'payer_commande.html', {'commande': commande})


@login_required
def historique_paiements(request):
    client = get_object_or_404(Client, utilisateur=request.user)
    paiements = Paiement.objects.filter(client=client).order_by('-date_paiement')
    return render(request, 'historique_paiements.html', {'paiements': paiements})


@login_required
def detail_paiement(request, paiement_id):
    paiement = get_object_or_404(Paiement, id=paiement_id, client__utilisateur=request.user)
    return render(request, 'detail_paiement.html', {'paiement': paiement})

