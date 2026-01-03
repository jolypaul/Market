from django.shortcuts import render, get_object_or_404, redirect
from django.shortcuts import render
from Publication.models import *
from Authentification.models import *
from GestionProduits.models import *

# Create your views here.
def creer_avis(request):
    client_id = request.session.get('user_id')

    if request.method == "POST":
        produit_id = request.POST.get('produit')
        note = request.POST.get('note')
        commentaire = request.POST.get('commentaire', '')

        client = Client.objects.get(utilisateur_id=client_id)
        produit = Produit.objects.get(id=produit_id)

        avis = Avis.objects.create(
            client=client,
            produit=produit,
            note=note,
            commentaire=commentaire
        )

    return redirect('dashboard_client_avis')

def creer_commentaire_commercant(request):
    client_id = request.session.get('user_id')
    client = get_object_or_404(Client, utilisateur_id=client_id)

    if request.method == "POST":
        commercant_id = request.POST.get('commercant')  # ID du commerçant sélectionné dans le form
        commentaire_text = request.POST.get('commentaire', '')

        commercant = get_object_or_404(Commercant, id=commercant_id)

        CommentaireCommercant.objects.create(
            client=client,
            commercant=commercant,
            commentaire=commentaire_text
        )

    return redirect('dashboard_client_avis')


def modifier_avis(request, avis_id):
    client_id = request.session.get('user_id')

    avis = get_object_or_404(Avis, id=avis_id, client__id=client_id)

    if request.method == "POST":
        produit_id = request.POST.get('produit')
        produit = Produit.objects.filter(id=produit_id).first()

        if not produit:
            return HttpResponse("Produit invalide", status=400)

        note = request.POST.get('note')
        commentaire = request.POST.get('commentaire', '')

        # Mise à jour
        avis.note = note
        avis.commentaire = commentaire
        avis.produit = produit   # ⚠️ On met l'objet PAS l'ID
        avis.save()

        return redirect('dashboard_client_avis')

    context = {
        "avis": avis
    }

    return render(request, "modifier_avis.html", context)

    
def supprimer_avis(request, avis_id):
    client_id = request.session.get('user_id')
    avis = get_object_or_404(Avis, id=avis_id, client__id=client_id)

    avis.delete()

    return redirect('dashboard_client_avis')

def modifier_commentaire_commercant(request, commentaire_id):
    client_id = request.session.get('user_id')
    client = get_object_or_404(Client, utilisateur_id=client_id)

    # Récupérer le commentaire uniquement si le client en est le propriétaire
    commentaire_obj = get_object_or_404(
        CommentaireCommercant, id=commentaire_id, client=client
    )

    if request.method == "POST":
        # Récupérer le commerçant choisi dans le formulaire
        commercant_id = request.POST.get('commercant')
        if not commercant_id:
            return HttpResponse("Commerçant invalide", status=400)

        commerçant = get_object_or_404(Commercant, id=commercant_id)

        texte_commentaire = request.POST.get('commentaire', '')

        # Mise à jour
        commentaire_obj.commentaire = texte_commentaire
        commentaire_obj.commercant = commerçant  # ⚠️ objet, PAS l'ID
        commentaire_obj.save()

        return redirect('dashboard_client_avis')

    context = {
        "avis": commentaire_obj
    }

    return render(request, "modifier_avis.html", context)


def creer_avis_commercant(request):
    client_id = request.session.get('user_id')
    client = get_object_or_404(Client, utilisateur_id=client_id)

    if request.method == "POST":
        commercant_id = request.POST.get('commercant')
        note = int(request.POST.get('note', 0))
        commentaire = request.POST.get('commentaire', '')

        commercant = get_object_or_404(Commercant, id=commercant_id)

        AvisCommercant.objects.create(
            client=client,
            commercant=commercant,  # ⚠️ Obligatoire
            note=note,
            commentaire=commentaire
        )

    return redirect('dashboard_client_avis')


def modifier_avis_commercant(request, avis_id):
    # Récupérer le client connecté
    client_id = request.session.get('user_id')
    client = get_object_or_404(Client, utilisateur_id=client_id)

    # Récupérer l'avis uniquement si le client en est le propriétaire
    avis = get_object_or_404(AvisCommercant, id=avis_id, client=client)

    if request.method == "POST":
        commercant_id = request.POST.get('commercant')
        note = int(request.POST.get('note', 0))
        commentaire = request.POST.get('commentaire', '')

        commercant = get_object_or_404(Commercant, id=commercant_id)

        # Mise à jour
        avis.commercant = commercant
        avis.note = note
        avis.commentaire = commentaire
        avis.save()

        return redirect('dashboard_client_avis')

    context = {
        'avis': avis
    }

    return render(request, 'modifier_avis_commercant.html', context)


def supprimer_avis_commercant(request, avis_id):
    client_id = request.session.get('user_id')
    client = get_object_or_404(Client, utilisateur_id=client_id)

    # Supprimer uniquement si le client est le propriétaire
    avis = get_object_or_404(AvisCommercant, id=avis_id, client=client)
    avis.delete()

    return redirect('dashboard_client_avis')



