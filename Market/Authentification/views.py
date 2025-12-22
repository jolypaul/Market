from django.shortcuts import render, redirect
import random
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from .models import Utilisateur, Client, Commercant, Administrateur, Livreur


def inscription(request):
    if request.method == 'POST':
        nom = request.POST.get('nom', '').strip()
        email = request.POST.get('email', '').strip()
        mot_de_passe = request.POST.get('password', '')
        userType = request.POST.get('userType', '').strip()
        telephone = request.POST.get('telephone', '').strip()
        adresse = request.POST.get('adresse', '').strip()
        boutique_nom = request.POST.get('boutique_nom', '').strip()
        adresse_boutique = request.POST.get('adresse_boutique', '').strip()
        zone_de_livraison = request.POST.get('zone_de_livraison', '').strip()

        # Validations
        if not nom or not email or not mot_de_passe or not userType:
            messages.error(request, 'Veuillez remplir tous les champs obligatoires.')
            return render(request, 'register.html')

        if Utilisateur.objects.filter(email=email).exists():
            messages.error(request, 'Cet email est déjà utilisé.')
            return render(request, 'register.html')

        if len(mot_de_passe) < 6:
            messages.error(request, 'Le mot de passe doit contenir au moins 6 caractères.')
            return render(request, 'register.html')

        try:
            # Créer l'utilisateur de base
            utilisateur = Utilisateur(
                nom=nom,
                email=email,
                motDePasse=make_password(mot_de_passe)
            )
            utilisateur.save()

            # Création du profil selon le type de compte
            if userType == 'client':
                if not telephone or not adresse:
                    messages.error(request, 'Le téléphone et l\'adresse sont obligatoires pour un client.')
                    utilisateur.delete()
                    return render(request, 'register.html')
                Client.objects.create(
                    utilisateur=utilisateur,
                    adresse=adresse,
                    telephone=telephone
                )
                messages.success(request, f'Compte client créé avec succès ! Bienvenue {nom}. Vous pouvez maintenant vous connecter.')

            elif userType == 'commercant':
                if not boutique_nom or not adresse_boutique:
                    messages.error(request, 'Le nom et l\'adresse de la boutique sont obligatoires pour un commerçant.')
                    utilisateur.delete()
                    return render(request, 'register.html')
                Commercant.objects.create(
                    utilisateur=utilisateur,
                    boutique_nom=boutique_nom,
                    adresse_boutique=adresse_boutique
                )
                messages.success(request, f'Compte commerçant créé avec succès ! Bienvenue {nom}. Vous pouvez maintenant vous connecter.')

            elif userType == 'administrateur':
                messages.error(request, 'Seul un administrateur existant peut créer un nouveau compte administrateur.')
                utilisateur.delete()
                return render(request, 'register.html')

            elif userType == 'livreur':
                messages.error(request, 'Seul un administrateur peut ajouter un livreur.')
                utilisateur.delete()
                return render(request, 'register.html')

            else:
                utilisateur.delete()
                messages.error(request, 'Type d\'utilisateur invalide.')
                return render(request, 'register.html')

            # Rediriger vers la page de connexion
            return redirect('connexion')

        except Exception as e:
            messages.error(request, f'Erreur lors de la création du compte : {str(e)}')
            if 'utilisateur' in locals() and utilisateur.id:
                utilisateur.delete()
            return render(request, 'register.html')

    return render(request, "register.html")


def connexion(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        mot_de_passe = request.POST.get('password')

        try:
            utilisateur = Utilisateur.objects.get(email=email)
        except Utilisateur.DoesNotExist:
            messages.error(request, 'Email ou mot de passe incorrect.')
            return render(request, 'login.html')

        if check_password(mot_de_passe, utilisateur.motDePasse):
            role = get_user_role(utilisateur)
            
            request.session['user_id'] = utilisateur.id
            request.session['nom'] = utilisateur.nom
            request.session['email'] = utilisateur.email
            request.session['role'] = role

            messages.success(request, f"Connexion réussie ! Bienvenue {utilisateur.nom}")
            
            # Redirection selon le rôle
            if role == "client":
                return redirect('accueil')  # ou votre page d'accueil client
            elif role == "commercant":
                return redirect('accueil')  # ou votre page d'accueil commerçant
            elif role in ["admin", "superadmin"]:
                return redirect('admin:index')  # Page admin Django
            elif role == "livreur":
                return redirect('accueil')  # ou votre page d'accueil livreur
            
            return redirect('accueil')

        else:
            messages.error(request, 'Email ou mot de passe incorrect.')
            return render(request, 'login.html')
    # Si la méthode n'est pas POST, afficher le formulaire de connexion
    return render(request, 'login.html')


def get_user_role(utilisateur):
    """Déterminer le rôle de l'utilisateur"""
    if hasattr(utilisateur, 'client'):
        return "client"
    if hasattr(utilisateur, 'commercant'):
        return "commercant"
    if hasattr(utilisateur, 'administrateur'):
        return utilisateur.administrateur.role
    if hasattr(utilisateur, 'livreur'):
        return "livreur"
    return "inconnu"


def mot_de_passe_oublie(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        # Chercher l'utilisateur
        try:
            utilisateur = Utilisateur.objects.get(email=email)
            # Générer un code à 6 chiffres
            code = random.randint(100000, 999999)
            request.session['reset_code'] = code
            request.session['reset_user_id'] = utilisateur.id
            request.session['reset_email'] = email

            # Envoyer l'e-mail
            send_mail(
                subject="Réinitialisation de mot de passe",
                message=f"Votre code de réinitialisation est : {code}",
                from_email="no-reply@monapp.com",
                recipient_list=[utilisateur.email],
            )
        except Utilisateur.DoesNotExist:
            # Pour la sécurité, on ne dit pas si l'email existe ou non
            # (évite de révéler les emails du système)
            pass
        
        # Afficher le même message pour tous les emails (existants ou non)
        messages.info(request, 'Si cet email est associé à un compte, vous recevrez un code de réinitialisation.')
        return redirect('verifier_code')
    
    return render(request, 'password_reset_request.html')


def verifier_code(request):
    if request.method == 'POST':
        code_saisi = request.POST.get('code', '').strip()
        reset_code = request.session.get('reset_code')
        
        if not reset_code:
            messages.error(request, 'Session expirée. Veuillez recommencer.')
            return redirect('mot_de_passe_oublie')
        
        if str(code_saisi) == str(reset_code):
            return redirect('reinitialiser_mdp')
        else:
            messages.error(request, 'Code incorrect.')
            return render(request, 'verify_code.html')

    return render(request, 'verify_code.html')


def reinitialiser_mdp(request):
    user_id = request.session.get('reset_user_id')
    if not user_id:
        return redirect('mot_de_passe_oublie')

    utilisateur = Utilisateur.objects.get(id=user_id)

    if request.method == 'POST':
        nouveau_mdp = request.POST.get('motdepasse')
        utilisateur.motDePasse = make_password(nouveau_mdp)
        utilisateur.save()

        # Supprimer les infos de session
        request.session.pop('reset_code', None)
        request.session.pop('reset_user_id', None)

        messages.success(request, "Mot de passe réinitialisé avec succès ! Veuillez vous connecter.")
        return redirect('connexion')

    return render(request, 'reset_password.html')


def mwp(request):
    """Redirection vers la page de réinitialisation de mot de passe"""
    return render(request, 'password_reset_request.html')


def logout(request):
    """Déconnecter l'utilisateur"""
    request.session.flush()
    messages.success(request, "Vous avez été déconnecté.")
    return redirect('connexion')
