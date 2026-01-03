from django.shortcuts import render, get_object_or_404, redirect
from .models import Categorie,Produit
from django.contrib import messages
from django.db.models.deletion import ProtectedError
from Authentification.models import Commercant,Client

# Create your views here.
def categorie_Save(request):
    if request.method=='POST':
        nom = request.POST.get('nom')
        description = request.POST.get('description')

        if(nom == '' or description == ""):
            return render (request, 'categorie_form.html', {'error':'Tous les champs sont obligatoires.'})
        if( Categorie.objects.filter(nom=nom).exists()):
            return render (request, 'categorie_form.html', {'error':'Cette catégorie existe déjà.'})
        else:
            categorie = Categorie(nom=nom, description=description)
            commercant_nom_connecter = Commercant.objects.get(utilisateur__email=request.session.get('email'))
            comerce = Commercant.objects.filter(id=commercant_nom_connecter.id)
            categorie.save()
            ensemble = Categorie.objects.all()
            return redirect(request, 'produit_form.html', {
                'ensemble': ensemble,
                'comerce': comerce,
                'commercant_nom_connecter':commercant_nom_connecter,
            })
    return redirect(request, 'categorie_form.html')

def crate_produit(request):
   # if 'user_id' not in request.session:
   #     messages.error(request, "Vous devez vous connecter.")
   #     return render(request,'login.html',{'messages':messages})
   # ele:
    ensemble = Categorie.objects.all()
    commercant_nom_connecter = Commercant.objects.get(utilisateur__email=request.session.get('email'))
    comerce = Commercant.objects.filter(id=commercant_nom_connecter.id)
    
    if request.method == 'POST':
        nom = request.POST.get('nom')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        prix = request.POST.get('prix')
        quantite_en_stock = request.POST.get('quantite_en_stock')
        categorie_id = request.POST.get('categorie_id')
        commerçant_id = request.POST.get('Commercant_id')
        
        context = {
            'ensemble': ensemble,
            'commercant_nom_connecter': commercant_nom_connecter,
            'comerce': comerce
        }
        
        if not nom or not prix or not quantite_en_stock or not categorie_id:
            context['error'] = 'Tous les champs obligatoires doivent être remplis.'
            return render(request, 'produit_form.html', context)
        try:
            prix = float(prix)
            quantite_en_stock = int(quantite_en_stock)
        except:
            context['error'] = 'Le prix et la quantité doivent être des valeurs numériques.'
            return render(request, 'produit_form.html', context)
        if prix <= 0:
            context['error'] = 'Le prix doit être supérieur à 0.'
            return render(request, 'produit_form.html', context)
        if quantite_en_stock < 0:
            context['error'] = 'La quantité ne peut pas être négative.'
            return render(request, 'produit_form.html', context)
        if Produit.objects.filter(nom=nom, categorie_id=categorie_id).exists():
            context['error'] = 'Ce produit existe déjà.'
            return render(request, 'produit_form.html', context)
        
        produit = Produit(
            nom=nom,
            description=description,
            image=image,
            prix=prix,
            quantite_en_stock=quantite_en_stock,
            categorie_id_id=categorie_id,
            Commercant_id_id=commerçant_id
        )
        produit.save()
        context['success'] = 'Produit ajouté avec succès.'
        return render(request, 'produit_form.html', context)
    
    return render(request, "produit_form.html", {
        'ensemble': ensemble,
        'commercant_nom_connecter': commercant_nom_connecter,
        'comerce': comerce
    })
def liste_produits(request):
    produits = Produit.objects.all()
    return render(request, 'liste_produits.html', {'produits': produits})

def detail_produit(request, produit_id):
    try:
        produit = Produit.objects.get(id=produit_id)
    except Produit.DoesNotExist:
        return render(request, 'detail_produit.html', {'error': 'Produit non trouvé.'})

    return render(request, 'detail_produit.html', {'produit': produit})

def modifierProduit(request, produit_id):
    try:
        produit = Produit.objects.get(id=produit_id)
    except Produit.DoesNotExist:
        return render(request, 'modifier_produit.html', {'error': 'Produit non trouvé.'})

    if request.method == 'POST':
        produit.nom = request.POST.get('nom')
        produit.description = request.POST.get('description')
        if 'image' in request.FILES:
            produit.image = request.FILES['image']
        produit.prix = request.POST.get('prix')
        produit.quantite_en_stock = request.POST.get('quantite_en_stock')
        produit.categorie_id_id = request.POST.get('categorie_id')
        produit.Commercant_id_id = request.POST.get('Commercant_id')
        produit.save()
        return render(request, 'produit_update.html', {'produit': produit, 'success': 'Produit modifié avec succès.'})

    return render(request, 'produit_update.html', {'produit': produit})

def supprimer_produit(request, produit_id):
    try:
        produit = Produit.objects.get(id=produit_id)
        produit.delete()
        produits = Produit.objects.all()
        messages.success(request, 'Produit supprimé avec succès.')
        return render(request, 'page_produits.html', {'produits': produits})
    except ProtectedError:
        produits = Produit.objects.all()
        messages.error(request, 'Impossible de supprimer ce produit car il est référencé dans une ou plusieurs commandes. Veuillez d\'abord supprimer les commandes associées.')
        return render(request, 'page_produits.html', {'produits': produits})
    except Produit.DoesNotExist:
        produits = Produit.objects.all()
        messages.error(request, 'Produit non trouvé.')
        return render(request, 'page_produits.html', {'produits': produits})
    
def modifier_categorie(request, categories_id):
    categorie = get_object_or_404(Categorie, id=categories_id)

    if request.method == 'POST':
        categorie.nom = request.POST.get('nom')
        categorie.description = request.POST.get('description')
        categorie.save()
        return render(request,'categorie_update.html', {'categories': categorie, 'success': 'Catégorie modifiée avec succès.'})

    return render(request, 'categorie_update.html', {'categories': categorie})

def supprimer_categorie(request, cat_id):
    try:
        categorie = get_object_or_404(Categorie, id=cat_id)
        categorie.delete()
        categories = Categorie.objects.all()
        return render(request, 'page_categorie.html', {'categories': categories, 'success': 'Catégorie supprimée avec succès.'})
    except Categorie.DoesNotExist:
        categories = Categorie.objects.all()
        return render(request, 'page_categorie.html', {'categories': categories, 'error': 'Catégorie non trouvée.'})
    
def liste_categories(request):
    categories = Categorie.objects.all()
    return render(request, 'page_categorie.html', {'categories': categories})


def page_categories(request,cat_id):
    categories = get_object_or_404(Categorie,id=cat_id)
    return render(request, 'categorie_update.html', {'categories': categories})