from django.shortcuts import render
from GestionProduits.models import Categorie,Produit
from Favoris.models import Favori
from django.contrib import messages
from Publication.models import Avis, CommentaireCommercant, AvisCommercant
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
        commercant_nom_connecter = Commercant.objects.get(utilisateur__email=request.session.get('email'))
        comerce = Commercant.objects.filter(id=commercant_nom_connecter.id)
        print(commercant_nom_connecter.id)
        return render(request, 'produit_form.html', {'ensemble': ensemble, 'comerce':comerce,'commercant_nom_connecter':commercant_nom_connecter})
    
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
        email = request.session.get('email')
        commercant = Commercant.objects.get(utilisateur__email=email)
        total_produit = Produit.objects.filter(Commercant_id=commercant).count()
        produits = Produit.objects.filter(Commercant_id__utilisateur__email=request.session.get('email'))
        categorie = Categorie.objects.all()
        total_categorie = Categorie.objects.count()
        total_commercant = Commercant.objects.count()
        total_produit_faible = Produit.objects.filter(quantite_en_stock__lte=10).count()
        return render(request, 'page_produits.html', {'total_produit_faible':total_produit_faible,'total_commercant':total_commercant,'total_categorie':total_categorie,'produits': produits,'categorie':categorie,'total_produit':total_produit})


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
    
def call_profil(request):
    emaile = request.session.get('email')
    role = request.session.get('role', 'default')
    utilisateur = Utilisateur.objects.get(email=emaile)
    role = request.session.get('role')

    if role == "client":
        layout = "base_client.html"
    elif role == "commercant":
        layout = "base_commercant.html"
    elif role == "livreur":
        layout = "base_livreur.html"
    else:
        layout = "base.html"

    return render(request, "profil.html", {"layout": layout,'utilisateur':utilisateur,'role':role})

def call_form_update_profil(request):
    role = request.session.get('role')
    utilisateur = Utilisateur.objects.get(email=request.session.get('email'))
    return render(request,'modifier_profil.html',{'utilisateur':utilisateur,'role':role})

def Dashboard_client(request):
    if request.session.get('role') != 'client':
        messages.error(request, "Accès refusé : seuls les clients peuvent acceder a cette page.")
        return render(request,'login.html',{'messages':messages.error})
    else:
        email = request.session.get('email')
        utilisateur = Utilisateur.objects.filter(email=email).first()
        return render(request,'dashboard_client.html',{'utilisateur':utilisateur})
    
def Dashboard_vendeur(request):
    if request.session.get('role') != 'commercant':
        messages.error(request, "Accès refusé : seuls les commerçants peuvent créer un produit.")
        return render(request,'login.html',{'messages':messages.error})
    else:
        return render(request,'dashboard_commercant.html')

def Dashboard_Livreur(request):
    if request.session.get('role') != 'livreur':
        messages.error(request, "Accès refusé : seuls les Livreurs peuvent acceder á cette espace.")
        return render(request,'login.html',{'messages':messages.error})
    else:
        return render(request,'dashboard_livreur.html')

def tout_les_produits(request):
    categorie = Categorie.objects.all()
    produits = Produit.objects.all()
    return render(request, 'liste_produits.html', {'produits': produits,'categorie':categorie})


# views.py


def dashboard_client_avis(request):
    client_id = request.session.get('user_id')
    if not client_id:
        return redirect('connexion')

    client = Client.objects.get(utilisateur_id=client_id)

    mes_avis = Avis.objects.filter(client=client).select_related('produit')
    mes_commentaires = CommentaireCommercant.objects.filter(
        client=client
    ).select_related('commercant__utilisateur')
    mes_avis_commercant = AvisCommercant.objects.filter(
        client=client
    ).select_related('commercant__utilisateur')

    produits_achetes = Produit.objects.all()
    # Pas de relation Produit ← Commande
    commerçants_connus = Commercant.objects.all()

    context = {
        'mes_avis': mes_avis,
        'mes_commentaires': mes_commentaires,
        'produits_achetes':produits_achetes,
        'mes_avis_commercant': mes_avis_commercant,
        'avis_count': mes_avis.count() + mes_avis_commercant.count(),
        'commerçants_connus': commerçants_connus,
    }

    return render(request, 'avis_dashboard_client.html', context)


def modelAvis(request):
    return render(request, 'avis_modals_client.html')
