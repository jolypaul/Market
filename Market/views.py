from django.shortcuts import redirect, render
from GestionProduits.models import Categorie,Produit
from Favoris.models import Favori
from Commande.models import Commande, ArticleCommande
from Paiement.models import Paiement
from Panier.models import Panier
from django.db.models import Avg, Sum, Count
import datetime
import json
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
        # Gather client object
        try:
            client = Client.objects.get(utilisateur__email=email)
        except Client.DoesNotExist:
            client = None

        # Basic stats
        commandes_total = Commande.objects.filter(client=client).count() if client else 0
        commandes_livrees = Commande.objects.filter(client=client, statut='livree').count() if client else 0
        commandes_en_attente = Commande.objects.filter(client=client).filter(statut__in=['en_attente','en_cours']).count() if client else 0

        # Average rating from Avis
        avg_note = Avis.objects.filter(client=client).aggregate(avg=Avg('note'))['avg'] if client else None
        note_moyenne = round(avg_note, 1) if avg_note is not None else None
        avis_count = Avis.objects.filter(client=client).count() + AvisCommercant.objects.filter(client=client).count() if client else 0

        # Favorites and cart
        favoris_count = Favori.objects.filter(client=client).count() if client else 0
        try:
            panier = Panier.objects.get(client=client)
            panier_items = panier.get_total_items()
        except Exception:
            panier_items = 0

        # Recent orders
        recent_orders = Commande.objects.filter(client=client).order_by('-date_commande')[:5] if client else []

        # Orders per month (last 12 months)
        today = datetime.date.today()
        months = []
        orders_monthly = []
        for i in range(11, -1, -1):
            m = (today.replace(day=1) - datetime.timedelta(days=1)).replace(day=1) - datetime.timedelta(days=0)
            target = today - datetime.timedelta(days=30*i)
            year = target.year
            month = target.month
            months.append(target.strftime('%b'))
            orders_monthly.append(Commande.objects.filter(client=client, date_commande__year=year, date_commande__month=month).count() if client else 0)

        # Expenses by category
        cat_qs = ArticleCommande.objects.filter(commande__client=client).values('produit__categorie_id__nom').annotate(total=Sum('sous_total')) if client else []
        categories = [c['produit__categorie_id__nom'] or 'Autres' for c in cat_qs]
        expenses = [float(c['total'] or 0) for c in cat_qs]

        context = {
            'utilisateur': utilisateur,
            'commandes_total': commandes_total,
            'commandes_livrees': commandes_livrees,
            'commandes_en_attente': commandes_en_attente,
            'note_moyenne': note_moyenne,
            'avis_count': avis_count,
            'favoris_count': favoris_count,
            'panier_items': panier_items,
            'recent_orders': recent_orders,
            'months_labels': months,
            'orders_monthly': orders_monthly,
            'categories_labels': categories,
            'expenses_data': expenses,
            'orders_monthly_json': json.dumps(orders_monthly),
            'months_labels_json': json.dumps(months),
            'categories_labels_json': json.dumps(categories),
            'expenses_data_json': json.dumps(expenses),
        }

        return render(request,'dashboard_client.html', context)
    
def Dashboard_vendeur(request):
    if request.session.get('role') != 'commercant':
        messages.error(request, "Accès refusé : seuls les commerçants peuvent créer un produit.")
        return render(request,'login.html',{'messages':messages.error})
    else:
        # Gather commerçant stats
        email = request.session.get('email')
        try:
            commercant = Commercant.objects.get(utilisateur__email=email)
        except Commercant.DoesNotExist:
            commercant = None

        produits_count = Produit.objects.filter(Commercant_id=commercant).count() if commercant else 0
        # Total sales (confirmed commandes) for this commercant
        ventes = ArticleCommande.objects.filter(produit__Commercant_id=commercant, commande__statut='confirmee').aggregate(total=Sum('sous_total')) if commercant else {'total': 0}
        chiffre_affaires = ventes['total'] or 0
        commandes_count = ArticleCommande.objects.filter(produit__Commercant_id=commercant).values('commande').distinct().count() if commercant else 0

        # Top products by quantity sold
        top_products_qs = ArticleCommande.objects.filter(produit__Commercant_id=commercant).values('produit__nom').annotate(qty=Sum('quantite')).order_by('-qty')[:5] if commercant else []
        avg_commercant = AvisCommercant.objects.filter(commercant=commercant).aggregate(avg=Avg('note'))['avg'] if commercant else None
        avg_commercant = round(avg_commercant,1) if avg_commercant is not None else None
        # Recent orders for this commercant
        recent_orders_commercant = Commande.objects.filter(articles__produit__Commercant_id=commercant).distinct().order_by('-date_commande')[:5] if commercant else []

        # Daily sales for last 30 days
        today = datetime.date.today()
        sales_days = []
        sales_daily = []
        for i in range(29, -1, -1):
            target_date = today - datetime.timedelta(days=i)
            sales_days.append(str(i + 1))
            daily_total = ArticleCommande.objects.filter(
                produit__Commercant_id=commercant,
                commande__statut='confirmee',
                commande__date_commande__date=target_date
            ).aggregate(total=Sum('sous_total'))['total'] or 0
            sales_daily.append(float(daily_total))

        # Top categories by sales amount
        cat_sales = ArticleCommande.objects.filter(
            produit__Commercant_id=commercant,
            commande__statut='confirmee'
        ).values('produit__categorie_id__nom').annotate(total=Sum('sous_total')).order_by('-total')[:5] if commercant else []
        categories_top = [c['produit__categorie_id__nom'] or 'Autres' for c in cat_sales]
        categories_data = [float(c['total'] or 0) for c in cat_sales]

        context = {
            'produits_count': produits_count,
            'chiffre_affaires': chiffre_affaires,
            'commandes_count': commandes_count,
            'top_products': top_products_qs,
            'recent_orders_commercant': recent_orders_commercant,
            'avg_commercant': avg_commercant,
            'sales_days': sales_days,
            'sales_daily': sales_daily,
            'categories_top': categories_top,
            'categories_data': categories_data,
            'sales_daily_json': json.dumps(sales_daily),
            'sales_days_json': json.dumps(sales_days),
            'categories_top_json': json.dumps(categories_top),
            'categories_data_json': json.dumps(categories_data),
        }
        return render(request,'dashboard_commercant.html', context)

def Dashboard_Livreur(request):
    if request.session.get('role') != 'livreur':
        messages.error(request, "Accès refusé : seuls les Livreurs peuvent acceder á cette espace.")
        return render(request,'login.html',{'messages':messages.error})
    else:
        # Simple delivery stats
        commandes_a_livrer = Commande.objects.filter(statut__in=['en_cours','expediee']).count()
        commandes_livre = Commande.objects.filter(statut='livree').count()
        context = {
            'commandes_a_livrer': commandes_a_livrer,
            'commandes_livre': commandes_livre,
        }
        return render(request,'dashboard_livreur.html', context)

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
