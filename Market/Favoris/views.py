from django.shortcuts import render
from .models import Favori
from GestionProduits.models import Produit
from Authentification.models import Client
from django.shortcuts import get_object_or_404, redirect

# Create your views here.
def retirer_favori(request, produit_id):
    fav = get_object_or_404(Favori, produit_id=produit_id)
    if(fav.client.id != request.session.get('user_id')):
        return redirect('login.html', {'error': "Vous n'êtes pas autorisé à effectuer cette action."})
    else:
        fav.delete()
        return redirect('favoris.html')
    
def ajouter_favori(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)

    client_id = request.session.get('user_id')
    if not client_id:
        return redirect('login')  

    client = get_object_or_404(Client, id=client_id)

    if Favori.objects.filter(client=client, produit=produit).exists():
        return render(request, 'favoris.html', {'error': "Ce produit est déjà dans vos favoris."})

    Favori.objects.create(client=client, produit=produit)

    return redirect('appeler_page_favorie')

def favorie_client(request):
    Client = request.session.get('user_id')
    fav = Favori.objects.get(Client=Client)
    return render(request,'favoris.html',)