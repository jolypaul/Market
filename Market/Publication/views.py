from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Publication
from Authentification.models import Commercant


def afficher_publications(request):
    publications = Publication.objects.all().order_by('-date_publication')
    return render(request, 'afficher_publications.html', {'publications': publications})


@login_required
def ajouter_publication(request):
    try:
        commercant = Commercant.objects.get(utilisateur=request.user)
    except Commercant.DoesNotExist:
        messages.error(request, "Vous devez être un commerçant pour publier.")
        return redirect('afficher_publications')
    
    if request.method == 'POST':
        titre = request.POST.get('titre')
        contenu = request.POST.get('contenu')
        
        publication = Publication.objects.create(
            titre=titre,
            contenu=contenu,
            auteur=commercant,
        )
        messages.success(request, "Publication créée avec succès!")
        return redirect('afficher_publications')
    
    return render(request, 'ajouter_publication.html')


@login_required
def modifier_publication(request, publication_id):
    publication = get_object_or_404(Publication, id=publication_id)
    
    # Vérifier que c'est l'auteur
    if publication.auteur.utilisateur != request.user:
        messages.error(request, "Vous n'êtes pas autorisé à modifier cette publication.")
        return redirect('afficher_publications')
    
    if request.method == 'POST':
        publication.titre = request.POST.get('titre')
        publication.contenu = request.POST.get('contenu')
        publication.save()
        messages.success(request, "Publication modifiée avec succès!")
        return redirect('afficher_publications')
    
    return render(request, 'modifier_publication.html', {'publication': publication})


@login_required
def supprimer_publication(request, publication_id):
    publication = get_object_or_404(Publication, id=publication_id)
    
    # Vérifier que c'est l'auteur
    if publication.auteur.utilisateur != request.user:
        messages.error(request, "Vous n'êtes pas autorisé à supprimer cette publication.")
        return redirect('afficher_publications')
    
    publication.delete()
    messages.success(request, "Publication supprimée.")
    return redirect('afficher_publications')


