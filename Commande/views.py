from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from Authentification.models import Client
from GestionProduits.models import Produit
from Panier.models import Panier, ArticlePanier
from .models import Commande, ArticleCommande
from Paiement.models import Paiement


def creer_commande(request):
    """Crée une commande à partir du panier"""
    from django.db import transaction as db_transaction
    
    if request.session.get('role') != 'client':
        messages.error(request, "Accès refusé")
        return redirect('login')
    
    user_id = request.session.get('user_id')
    
    try:
        client = Client.objects.get(utilisateur_id=user_id)
    except Client.DoesNotExist:
        messages.error(request, "Erreur : client non trouvé")
        return redirect('Dashboard_client')
    
    panier = Panier.objects.filter(client=client).first()
    
    if not panier or panier.articles.count() == 0:
        messages.error(request, "Votre panier est vide")
        return redirect('vue_panier')
    
    if request.method == 'POST':
        adresse_livraison = request.POST.get('adresse_livraison', client.adresse)
        notes = request.POST.get('notes', '')
        total = panier.get_total()
        
        if not adresse_livraison:
            messages.error(request, "L'adresse de livraison est obligatoire")
            return redirect('vue_panier')
        
        # Vérifier que les produits sont toujours en stock
        for article in panier.articles.all():
            if article.quantite > article.produit.quantite_en_stock:
                messages.error(
                    request,
                    f"Stock insuffisant pour '{article.produit.nom}'. "
                    f"Disponible: {article.produit.quantite_en_stock}"
                )
                return redirect('vue_panier')
        
        try:
            with db_transaction.atomic():
                # Créer la commande
                commande = Commande.objects.create(
                    client=client,
                    total=total,
                    adresse_livraison=adresse_livraison,
                    notes=notes,
                    statut='en_attente'
                )
                
                # Copier les articles du panier vers la commande
                for article_panier in panier.articles.all():
                    ArticleCommande.objects.create(
                        commande=commande,
                        produit=article_panier.produit,
                        quantite=article_panier.quantite,
                        prix_unitaire=article_panier.prix_unitaire,
                        sous_total=article_panier.get_subtotal()
                    )
                    
                    # Réduire le stock du produit
                    produit = article_panier.produit
                    produit.quantite_en_stock -= article_panier.quantite
                    produit.save()
                
                # Vider le panier après création de la commande
                panier.articles.all().delete()
                
                # Créer un paiement en attente
                paiement = Paiement.objects.create(
                    reference=f"PAY-{commande.id}-{commande.date_commande.timestamp()}",
                    client=client,
                    montant=commande.total,
                    commande=commande,
                    statut='en_cours',
                    type_paiement='carte'  # Par défaut
                )
                
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"[COMMANDE] Commande créée: {commande.id} | Paiement: {paiement.id} | Montant: {commande.total} FCFA")
                
                messages.success(request, "Commande créée avec succès!")
                return redirect('paiement_checkout', paiement_id=paiement.id)
        
        except db_transaction.TransactionError as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"[COMMANDE] Erreur de transaction: {str(e)}")
            messages.error(request, "Erreur lors de la création de la commande")
            return redirect('vue_panier')
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"[COMMANDE] Erreur: {str(e)}")
            messages.error(request, "Une erreur est survenue")
            return redirect('vue_panier')
    
    context = {
        'panier': panier,
        'articles': panier.articles.all(),
        'client': client,
        'total': panier.get_total(),
        'layout': 'base_client.html'
    }
    
    return render(request, 'checkout.html', context)


def creer_commande_api(request):
    """API: crée une commande à partir du panier DB puis crée un paiement et retourne l'id du paiement"""
    from django.http import JsonResponse
    from django.db import transaction as db_transaction
    import logging
    
    logger = logging.getLogger(__name__)
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Méthode non autorisée'}, status=405)

    if request.session.get('role') != 'client':
        return JsonResponse({'success': False, 'message': 'Accès refusé'}, status=403)

    user_id = request.session.get('user_id')
    try:
        client = Client.objects.get(utilisateur_id=user_id)
    except Client.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Client introuvable'}, status=404)

    panier = Panier.objects.filter(client=client).first()
    if not panier or panier.articles.count() == 0:
        return JsonResponse({'success': False, 'message': 'Panier vide'}, status=400)

    # Utiliser l'adresse du client si disponible
    adresse_livraison = getattr(client, 'adresse', '') or ''

    # Vérifier le stock
    for article in panier.articles.select_related('produit').all():
        if article.quantite > article.produit.quantite_en_stock:
            return JsonResponse({'success': False, 'message': f"Stock insuffisant pour {article.produit.nom}"}, status=400)

    try:
        with db_transaction.atomic():
            # Créer la commande
            total = panier.get_total()
            commande = Commande.objects.create(
                client=client,
                total=total,
                adresse_livraison=adresse_livraison,
                statut='en_attente'
            )

            # Copier articles et décrémenter le stock
            for article_panier in panier.articles.select_related('produit').all():
                ArticleCommande.objects.create(
                    commande=commande,
                    produit=article_panier.produit,
                    quantite=article_panier.quantite,
                    prix_unitaire=article_panier.prix_unitaire,
                    sous_total=article_panier.get_subtotal()
                )
                produit = article_panier.produit
                produit.quantite_en_stock -= article_panier.quantite
                produit.save()

            # Vider le panier après création de la commande
            panier.articles.all().delete()

            # Créer paiement
            paiement = Paiement.objects.create(
                reference=f"PAY-{commande.id}",
                client=client,
                montant=commande.total,
                commande=commande,
                statut='en_cours',
                type_paiement='carte'
            )
            
            logger.info(f"[COMMANDE API] Commande créée: {commande.id} | Paiement: {paiement.id} | Montant: {commande.total} FCFA")

            return JsonResponse({'success': True, 'paiement_id': str(paiement.id), 'redirect_url': f'/paiement/checkout/{paiement.id}/'})
    
    except db_transaction.TransactionError as e:
        logger.error(f"[COMMANDE API] Erreur de transaction: {str(e)}")
        return JsonResponse({'success': False, 'message': 'Erreur lors de la création de la commande'}, status=500)
    except Exception as e:
        logger.error(f"[COMMANDE API] Erreur: {str(e)}")
        return JsonResponse({'success': False, 'message': 'Erreur serveur'}, status=500)


def liste_commandes(request):
    """Affiche la liste des commandes du client"""
    if request.session.get('role') != 'client':
        messages.error(request, "Accès refusé")
        return redirect('login')
    
    user_id = request.session.get('user_id')
    
    try:
        client = Client.objects.get(utilisateur_id=user_id)
    except Client.DoesNotExist:
        messages.error(request, "Erreur : client non trouvé")
        return redirect('Dashboard_client')
    
    commandes = Commande.objects.filter(client=client).prefetch_related('articles')
    
    context = {
        'commandes': commandes,
        'layout': 'base_client.html'
    }
    
    return render(request, 'liste_commandes.html', context)


def detail_commande(request, commande_id):
    """Affiche les détails d'une commande"""
    if request.session.get('role') != 'client':
        messages.error(request, "Accès refusé")
        return redirect('login')
    
    user_id = request.session.get('user_id')
    
    try:
        client = Client.objects.get(utilisateur_id=user_id)
    except Client.DoesNotExist:
        messages.error(request, "Erreur : client non trouvé")
        return redirect('Dashboard_client')
    
    commande = get_object_or_404(Commande, id=commande_id, client=client)
    articles = commande.articles.all()
    
    context = {
        'commande': commande,
        'articles': articles,
        'layout': 'base_client.html'
    }
    
    return render(request, 'detail_commande.html', context)


def annuler_commande(request, commande_id):
    """Annule une commande (si possible)"""
    if request.session.get('role') != 'client':
        messages.error(request, "Accès refusé")
        return redirect('login')
    
    user_id = request.session.get('user_id')
    
    try:
        client = Client.objects.get(utilisateur_id=user_id)
    except Client.DoesNotExist:
        messages.error(request, "Erreur : client non trouvé")
        return redirect('Dashboard_client')
    
    commande = get_object_or_404(Commande, id=commande_id, client=client)
    
    # On peut seulement annuler les commandes en attente
    if commande.statut not in ['en_attente', 'confirmee']:
        messages.error(request, "Vous ne pouvez pas annuler cette commande")
        return redirect('detail_commande', commande_id=commande.id)
    
    # Rembourser le stock
    for article in commande.articles.all():
        produit = article.produit
        produit.quantite_en_stock += article.quantite
        produit.save()
    
    # Mettre à jour le statut
    commande.statut = 'annulee'
    commande.save()
    
    # Mettre à jour le paiement
    paiement = Paiement.objects.filter(commande=commande).first()
    if paiement:
        paiement.statut = 'annule'
        paiement.save()
    
    messages.success(request, "Commande annulée avec succès")
    return redirect('liste_commandes')
