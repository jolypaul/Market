from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Livraison, EvaluationLivraison


def afficher_livraisons(request):
    livraisons = Livraison.objects.all()
    return render(request, 'afficher_livraisons.html', {'livraisons': livraisons})


@login_required
def suivre_livraison(request, livraison_id):
    livraison = get_object_or_404(Livraison, id=livraison_id)
    return render(request, 'suivre_livraison.html', {'livraison': livraison})


@login_required
def evaluer_livraison(request, livraison_id):
    livraison = get_object_or_404(Livraison, id=livraison_id, client__utilisateur=request.user)

    if request.method == 'POST':
        note = int(request.POST.get('note', 0))
        commentaire = request.POST.get('commentaire', '')
        
        evaluation, created = EvaluationLivraison.objects.get_or_create(
            livraison=livraison,
            client=livraison.client,
            defaults={'note': note, 'commentaire': commentaire}
        )
        if not created:
            evaluation.note = note
            evaluation.commentaire = commentaire
            evaluation.save()
        
        messages.success(request, "Évaluation enregistrée!")
        return redirect('suivre_livraison', livraison_id=livraison.id)

    return render(request, 'evaluer_livraison.html', {'livraison': livraison})


@login_required
def accepter_livraison(request, livraison_id):
    livraison = get_object_or_404(Livraison, id=livraison_id, livreur__utilisateur=request.user)
    
    if livraison.statut == 'en_cours':
        livraison.statut = 'livree'
        livraison.save()
        messages.success(request, "Livraison marquée comme effectuée.")
    
    return redirect('suivre_livraison', livraison_id=livraison.id)





