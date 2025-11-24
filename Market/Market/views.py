from django.shortcuts import render
from GestionProduits.models import Categorie,Produit
from Favoris.models import Favori
from django.contrib import messages
from Authentification.models import Commercant,Client,Utilisateur

def login(request):
    request.session.flush()
    return render(request, 'login.html')

def register(request):
    return render(request, 'register.html')

def produit(request):
    if request.session.get('role') != 'commercant':
        messages.error(request, "Accès refusé : seuls les commerçants peuvent créer un produit.")
        return render(request,'login.html',{'messages':messages.error})
    else:
        ensemble = Categorie.objects.all()
        comerce = Commercant.objects.all()
        return render(request, 'produit_form.html', {'ensemble': ensemble, 'comerce':comerce})
    
def categorie(request):
        if request.session.get('role') != 'commercant':
            messages.error(request, "Accès refusé : seuls les commerçants peuvent créer un produit.")
            return render(request,'login.html',{'messages':messages.error})
        else:
            return render(request, 'categorie_form.html')


def page_produits(request):
    if request.session.get('role') != 'commercant':
        messages.error(request, "Accès refusé : seuls les commerçants peuvent créer un produit.")
        return render(request,'login.html',{'messages':messages.error})
    else:
        produits = Produit.objects.all()
        return render(request, 'page_produits.html', {'produits': produits})


def form_modifier_produit(request,id):
    categories=Categorie.objects.all()
    produit = Produit.objects.get(id=id)
    return render(request, 'produit_update.html',{'produit':produit,'categories':categories})

def appeler_page_favorie(request):
    if request.session.get('role') != 'client':
        messages.error(request, "Accès refusé : seuls les commerçants peuvent créer un produit.")
        return render(request,'login.html',{'messages':messages.error})
    else:
        produit= Produit.objects.all()
        #favories = Favori.objects.filter(client__id=request.session.get('user_id'))
        return render(request,'favoris.html',{'produits':produit})