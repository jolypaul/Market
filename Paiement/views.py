from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.db import transaction
from Authentification.models import Client
from Commande.models import Commande, ArticleCommande
from .models import Paiement, HistoriquePaiement
import json
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

# SYSTÈME DE PAIEMENT SIMULÉ (Mock/Test)
# Ce système permet de tester le flux complet sans Stripe
# En production, intégrez avec une véritable passerelle de paiement


def paiement_checkout(request, paiement_id):
    """Page de checkout pour le paiement (SIMULATION)"""
    if request.session.get('role') != 'client':
        messages.error(request, "Accès refusé")
        return redirect('login')
    
    user_id = request.session.get('user_id')
    
    try:
        client = Client.objects.get(utilisateur_id=user_id)
    except Client.DoesNotExist:
        messages.error(request, "Erreur : client non trouvé")
        return redirect('Dashboard_client')
    
    try:
        paiement = Paiement.objects.get(id=paiement_id, client=client)
    except Paiement.DoesNotExist:
        messages.error(request, "Paiement non trouvé")
        return redirect('Dashboard_client')
    
    if paiement.statut not in ['en_cours', 'echec']:
        messages.error(request, "Ce paiement ne peut pas être modifié")
        return redirect('detail_commande', commande_id=paiement.commande.id)
    
    # Validate payment amount
    commande = paiement.commande
    total = commande.total
    
    context = {
        'paiement': paiement,
        'commande': commande,
        'client': client,
        'total': total,
        'layout': 'base_client.html'
    }
    
    return render(request, 'paiement_checkout_simple.html', context)



@require_http_methods(["POST"])
def confirmer_paiement(request, paiement_id):
    """Traite le paiement en simulation avec validation complète"""
    if request.session.get('role') != 'client':
        return JsonResponse({'success': False, 'message': 'Accès refusé'}, status=403)
    
    user_id = request.session.get('user_id')
    
    try:
        client = Client.objects.get(utilisateur_id=user_id)
    except Client.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Client non trouvé'}, status=404)
    
    try:
        paiement = Paiement.objects.get(id=paiement_id, client=client)
    except Paiement.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Paiement non trouvé'}, status=404)
    
    # Vérifier l'état du paiement
    if paiement.statut not in ['en_cours', 'echec']:
        return JsonResponse({
            'success': False, 
            'message': f'Paiement ne peut pas être traité (état actuel: {paiement.statut})'
        }, status=400)
    
    try:
        with transaction.atomic():
            type_resultat = request.POST.get('type_resultat', 'succes').lower()
            commande = paiement.commande
            
            logger.info(f"[PAIEMENT {paiement_id}] Simulation - Type: {type_resultat} | Montant: {commande.total} | Client: {client.utilisateur.nom}")
            
            # ========================================
            # SIMULATION 1: Carte refusée
            # ========================================
            if type_resultat == 'refusee':
                paiement.statut = 'echec'
                paiement.message_erreur = "Votre carte bancaire a été refusée par votre banque"
                paiement.save()
                
                HistoriquePaiement.objects.create(
                    paiement=paiement,
                    action='echec',
                    statut_avant='en_cours',
                    statut_apres='echec',
                    message="Simulation: Carte refusée par la banque"
                )
                
                logger.warning(f"[PAIEMENT {paiement_id}] REFUSÉ - Carte bancaire refusée")
                return JsonResponse({
                    'success': False,
                    'message': 'Paiement refusé - Votre carte bancaire a été refusée',
                    'error_type': 'card_declined',
                    'redirect_url': f'/paiement/erreur/?paiement_id={paiement.id}'
                }, status=402)
            
            # ========================================
            # SIMULATION 2: Erreur réseau
            # ========================================
            elif type_resultat == 'erreur':
                paiement.statut = 'echec'
                paiement.message_erreur = "Erreur de connexion au serveur de paiement. Veuillez réessayer."
                paiement.save()
                
                HistoriquePaiement.objects.create(
                    paiement=paiement,
                    action='echec',
                    statut_avant='en_cours',
                    statut_apres='echec',
                    message="Simulation: Erreur de connexion réseau"
                )
                
                logger.error(f"[PAIEMENT {paiement_id}] ERREUR RÉSEAU")
                return JsonResponse({
                    'success': False,
                    'message': 'Erreur de paiement - Veuillez réessayer ultérieurement',
                    'error_type': 'network_error',
                    'redirect_url': f'/paiement/erreur/?paiement_id={paiement.id}'
                }, status=500)
            
            # ========================================
            # SIMULATION 3: Paiement réussi (DEFAULT)
            # ========================================
            else:
                # Validation: vérifier que la commande a des articles
                articles = commande.articles.all()
                if not articles.exists():
                    return JsonResponse({
                        'success': False,
                        'message': 'La commande ne contient pas d\'articles'
                    }, status=400)
                
                # Vérifier que le montant est valide
                if commande.total <= 0:
                    return JsonResponse({
                        'success': False,
                        'message': 'Le montant de la commande est invalide'
                    }, status=400)
                
                paiement.statut = 'confirme'
                paiement.save()
                
                # Mettre à jour la commande
                commande.statut = 'confirmee'
                commande.save()
                
                HistoriquePaiement.objects.create(
                    paiement=paiement,
                    action='succes',
                    statut_avant='en_cours',
                    statut_apres='confirme',
                    message=f"Simulation: Paiement approuvé pour {commande.total} FCFA"
                )
                
                # Vider le panier du client après paiement réussi
                from Panier.models import Panier
                try:
                    panier = Panier.objects.get(client=client)
                    articles_count = panier.articles.count()
                    panier.articles.all().delete()
                    logger.info(f"[PANIER] Panier vidé après paiement confirmé ({articles_count} articles) (client: {client.utilisateur.id})")
                except Panier.DoesNotExist:
                    pass
                
                logger.info(f"[PAIEMENT {paiement_id}] SUCCÈS - Montant: {commande.total} FCFA | Commande: {commande.id}")
                return JsonResponse({
                    'success': True,
                    'message': 'Paiement approuvé avec succès!',
                    'redirect_url': f'/paiement/succes/?paiement_id={paiement.id}'
                }, status=200)
    
    except transaction.TransactionError as e:
        logger.error(f"[PAIEMENT {paiement_id}] ERREUR DE TRANSACTION: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Erreur lors du traitement de la transaction'
        }, status=500)
    
    except Exception as e:
        logger.error(f"[PAIEMENT {paiement_id}] ERREUR SERVEUR: {str(e)}")
        paiement.statut = 'echec'
        paiement.message_erreur = f"Erreur serveur: {str(e)[:100]}"
        paiement.save()
        
        return JsonResponse({
            'success': False,
            'message': 'Erreur lors du traitement du paiement'
        }, status=500)


def paiement_succes(request):
    """Page de succès de paiement"""
    paiement_id = request.GET.get('paiement_id')
    
    if not paiement_id:
        messages.error(request, "Paiement introuvable")
        return redirect('Dashboard_client')
    
    try:
        paiement = Paiement.objects.get(id=paiement_id)
        
        # Vérifier que le paiement est confirmé
        if paiement.statut != 'confirme':
            messages.error(request, "Ce paiement n'a pas été confirmé")
            return redirect('Dashboard_client')
        
        context = {
            'paiement': paiement,
            'commande': paiement.commande,
            'layout': 'base_client.html'
        }
        
        return render(request, 'paiement_succes.html', context)
    
    except Paiement.DoesNotExist:
        messages.error(request, "Paiement introuvable")
        return redirect('Dashboard_client')


def paiement_erreur(request):
    """Page d'erreur de paiement"""
    paiement_id = request.GET.get('paiement_id')
    
    if not paiement_id:
        messages.error(request, "Paiement introuvable")
        return redirect('Dashboard_client')
    
    try:
        paiement = Paiement.objects.get(id=paiement_id)
        
        # Vérifier que le paiement est en erreur
        if paiement.statut != 'echec':
            messages.warning(request, f"Statut du paiement: {paiement.get_statut_display()}")
        
        context = {
            'paiement': paiement,
            'commande': paiement.commande,
            'error_message': paiement.message_erreur or "Une erreur est survenue lors du paiement",
            'layout': 'base_client.html'
        }
        
        return render(request, 'paiement_erreur.html', context)
    
    except Paiement.DoesNotExist:
        messages.error(request, "Paiement introuvable")
        return redirect('Dashboard_client')
    
    except Paiement.DoesNotExist:
        messages.error(request, "Paiement introuvable")
        return redirect('Dashboard_client')

