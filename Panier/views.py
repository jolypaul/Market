from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.db import transaction
from decimal import Decimal
from GestionProduits.models import Produit
from Authentification.models import Client
from .models import Panier, ArticlePanier
import json
import logging

logger = logging.getLogger(__name__)


def get_or_create_panier(user_id):
    """Helper pour obtenir ou créer le panier d'un client"""
    try:
        utilisateur = Client.objects.get(utilisateur_id=user_id)
        panier, created = Panier.objects.get_or_create(client=utilisateur)
        return panier
    except Client.DoesNotExist:
        return None


def vue_panier(request):
    """Affiche le panier du client"""
    if request.session.get('role') != 'client':
        messages.error(request, "Accès refusé : seuls les clients peuvent consulter le panier.")
        return redirect('login')
    
    user_id = request.session.get('user_id')
    panier = get_or_create_panier(user_id)
    
    if not panier:
        messages.error(request, "Erreur : impossible de charger votre panier.")
        return redirect('Dashboard_client')
    
    # Si le panier DB est vide, rediriger vers la page des produits (supprime la page panier vide)
    if panier.articles.count() == 0:
        return redirect('tout_les_produits')
    
    articles = panier.articles.all().select_related('produit')
    total = panier.get_total()
    nombre_articles = panier.get_total_items()
    
    context = {
        'articles': articles,
        'panier': panier,
        'total': total,
        'nombre_articles': nombre_articles,
        'layout': 'base_client.html'
    }
    
    return render(request, 'panier.html', context)


@require_POST
def ajouter_panier(request, produit_id):
    """Ajoute un produit au panier"""
    if request.session.get('role') != 'client':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Accès refusé'}, status=403)
        messages.error(request, "Accès refusé : seuls les clients peuvent ajouter des produits.")
        return redirect('login')
    
    user_id = request.session.get('user_id')
    panier = get_or_create_panier(user_id)
    
    if not panier:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Erreur panier'}, status=500)
        messages.error(request, "Erreur : impossible de charger votre panier.")
        return redirect('Dashboard_client')
    
    try:
        produit = get_object_or_404(Produit, id=produit_id)
    except Exception as e:
        logger.error(f"Produit non trouvé: {produit_id}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Produit introuvable'}, status=404)
        messages.error(request, "Produit introuvable")
        return redirect('tout_les_produits')
    
    # Vérifier la disponibilité
    if produit.quantite_en_stock <= 0:
        msg = f"Le produit '{produit.nom}' n'est pas disponible."
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': msg}, status=400)
        messages.error(request, msg)
        return redirect(request.META.get('HTTP_REFERER', 'tout_les_produits'))
    
    quantite = int(request.POST.get('quantite', 1))
    
    if quantite <= 0:
        msg = "La quantité doit être au minimum 1."
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': msg}, status=400)
        messages.error(request, msg)
        return redirect(request.META.get('HTTP_REFERER', 'tout_les_produits'))
    
    if quantite > produit.quantite_en_stock:
        msg = f"Stock insuffisant. Disponible : {produit.quantite_en_stock}"
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': msg}, status=400)
        messages.error(request, msg)
        return redirect(request.META.get('HTTP_REFERER', 'tout_les_produits'))
    
    try:
        with transaction.atomic():
            # Vérifier si le produit existe déjà dans le panier
            article_existant = panier.articles.filter(produit=produit).first()
            
            if article_existant:
                nouvelle_quantite = article_existant.quantite + quantite
                if nouvelle_quantite > produit.quantite_en_stock:
                    msg = f"Stock insuffisant pour cette quantité. Maximum disponible: {produit.quantite_en_stock}"
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'message': msg}, status=400)
                    messages.error(request, msg)
                    return redirect(request.META.get('HTTP_REFERER', 'tout_les_produits'))
                
                article_existant.quantite = nouvelle_quantite
                article_existant.save()
                message = f"Quantité de '{produit.nom}' mise à jour"
                logger.info(f"[PANIER] Quantité augmentée pour {produit.nom} (user: {user_id})")
            else:
                ArticlePanier.objects.create(
                    panier=panier,
                    produit=produit,
                    quantite=quantite,
                    prix_unitaire=produit.prix
                )
                message = f"'{produit.nom}' ajouté au panier"
                logger.info(f"[PANIER] Produit ajouté: {produit.nom} (user: {user_id})")
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': message,
                    'total_articles': panier.get_total_items(),
                    'total': str(panier.get_total())
                })
            
            messages.success(request, message)
            return redirect(request.META.get('HTTP_REFERER', 'vue_panier'))
    
    except Exception as e:
        logger.error(f"Erreur lors de l'ajout au panier: {str(e)}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Erreur serveur'}, status=500)
        messages.error(request, "Une erreur est survenue")
        return redirect(request.META.get('HTTP_REFERER', 'vue_panier'))


@require_POST
def retirer_panier(request, article_id):
    """Retire un article du panier"""
    if request.session.get('role') != 'client':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Accès refusé'}, status=403)
        messages.error(request, "Accès refusé")
        return redirect('login')
    
    user_id = request.session.get('user_id')
    panier = get_or_create_panier(user_id)
    
    if not panier:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Erreur panier'}, status=500)
        messages.error(request, "Erreur panier")
        return redirect('Dashboard_client')
    
    try:
        article = get_object_or_404(ArticlePanier, id=article_id, panier=panier)
        produit_nom = article.produit.nom
        article.delete()
        
        logger.info(f"[PANIER] Produit retiré: {produit_nom} (user: {user_id})")
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f"'{produit_nom}' retiré du panier",
                'total_articles': panier.get_total_items(),
                'total': str(panier.get_total())
            })
        
        messages.success(request, f"'{produit_nom}' retiré du panier")
        return redirect('vue_panier')
    
    except Exception as e:
        logger.error(f"Erreur lors du retrait du panier: {str(e)}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Erreur serveur'}, status=500)
        messages.error(request, "Une erreur est survenue")
        return redirect('vue_panier')


@require_POST
def modifier_quantite_panier(request, article_id):
    """Modifie la quantité d'un article"""
    if request.session.get('role') != 'client':
        return JsonResponse({'success': False, 'message': 'Accès refusé'}, status=403)
    
    user_id = request.session.get('user_id')
    panier = get_or_create_panier(user_id)
    
    if not panier:
        return JsonResponse({'success': False, 'message': 'Erreur panier'}, status=500)
    
    try:
        article = get_object_or_404(ArticlePanier, id=article_id, panier=panier)
        nouvelle_quantite = int(request.POST.get('quantite', 1))
        
        if nouvelle_quantite <= 0:
            return JsonResponse({'success': False, 'message': 'Quantité invalide'}, status=400)
        
        if nouvelle_quantite > article.produit.quantite_en_stock:
            return JsonResponse({
                'success': False,
                'message': f"Stock insuffisant. Disponible : {article.produit.quantite_en_stock}"
            }, status=400)
        
        article.quantite = nouvelle_quantite
        article.save()
        
        logger.info(f"[PANIER] Quantité modifiée pour {article.produit.nom} -> {nouvelle_quantite} (user: {user_id})")
        
        return JsonResponse({
            'success': True,
            'message': 'Quantité mise à jour',
            'subtotal': str(article.get_subtotal()),
            'total': str(panier.get_total()),
            'total_articles': panier.get_total_items()
        })
    
    except Exception as e:
        logger.error(f"Erreur lors de la modification de quantité: {str(e)}")
        return JsonResponse({'success': False, 'message': 'Erreur serveur'}, status=500)


@require_POST
def vider_panier(request):
    """Vide complètement le panier"""
    if request.session.get('role') != 'client':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Accès refusé'}, status=403)
        messages.error(request, "Accès refusé")
        return redirect('login')
    
    user_id = request.session.get('user_id')
    panier = get_or_create_panier(user_id)
    
    if not panier:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Erreur panier'}, status=500)
        messages.error(request, "Erreur panier")
        return redirect('Dashboard_client')
    
    try:
        nombre_articles = panier.articles.count()
        panier.articles.all().delete()
        
        logger.info(f"[PANIER] Panier vidé ({nombre_articles} articles) (user: {user_id})")
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Panier vidé'})
        
        messages.success(request, "Panier vidé avec succès")
        return redirect('vue_panier')
    
    except Exception as e:
        logger.error(f"Erreur lors du vidage du panier: {str(e)}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Erreur serveur'}, status=500)
        messages.error(request, "Une erreur est survenue")
        return redirect('vue_panier')


@require_http_methods(['GET', 'POST'])
def sync_panier_from_localstorage(request):
    """API endpoint pour synchroniser le localStorage avec la DB"""
    if request.session.get('role') != 'client':
        return JsonResponse({'success': False, 'message': 'Accès refusé'}, status=403)
    
    if request.method == 'GET':
        # Retourner le panier actuel depuis la DB
        user_id = request.session.get('user_id')
        panier = get_or_create_panier(user_id)
        
        if not panier:
            return JsonResponse({'success': False, 'message': 'Erreur panier'}, status=500)
        
        articles = []
        for article in panier.articles.all():
            articles.append({
                'id': article.id,
                'productId': article.produit.id,
                'productName': article.produit.nom,
                'productPrice': float(article.prix_unitaire),
                'quantity': article.quantite,
                'subtotal': float(article.get_subtotal())
            })
        
        return JsonResponse({
            'success': True,
            'cart': articles,
            'total': float(panier.get_total()),
            'total_items': panier.get_total_items()
        })
    
    elif request.method == 'POST':
        # Synchroniser le panier du localStorage vers la DB
        user_id = request.session.get('user_id')
        panier = get_or_create_panier(user_id)
        
        if not panier:
            return JsonResponse({'success': False, 'message': 'Erreur panier'}, status=500)
        
        try:
            cart_data = json.loads(request.body).get('cart', [])
            
            with transaction.atomic():
                # Vider le panier existant
                panier.articles.all().delete()
                
                # Ajouter les nouveaux articles
                for item in cart_data:
                    try:
                        produit = Produit.objects.get(id=item.get('productId'))
                        
                        # Vérifier le stock
                        qty = int(item.get('quantity', 1))
                        if qty > produit.quantite_en_stock:
                            continue
                        
                        ArticlePanier.objects.create(
                            panier=panier,
                            produit=produit,
                            quantite=qty,
                            prix_unitaire=Decimal(str(item.get('productPrice', produit.prix)))
                        )
                    except Produit.DoesNotExist:
                        continue
                
                logger.info(f"[PANIER] Synchronisé depuis localStorage ({len(cart_data)} items) (user: {user_id})")
                
                return JsonResponse({
                    'success': True,
                    'message': f'{len(cart_data)} articles synchronisés',
                    'total': float(panier.get_total()),
                    'total_items': panier.get_total_items()
                })
        
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Format JSON invalide'}, status=400)
        except Exception as e:
            logger.error(f"Erreur de synchronisation panier: {str(e)}")
            return JsonResponse({'success': False, 'message': 'Erreur serveur'}, status=500)

