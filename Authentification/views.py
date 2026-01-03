from django.shortcuts import render, redirect
import random
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from django.contrib.auth import authenticate,login
from django.contrib.auth.hashers import make_password
from rest_framework.response import Response   
from django.core.mail import send_mail
#import du module pour les tokens
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Utilisateur, Client, Commercant, Administrateur, Livreur

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def inscription(request):
    if request.method == 'POST':
        nom = request.POST.get('nom')
        email = request.POST.get('email')
        mot_de_passe = request.POST.get('password')
        userType = request.POST.get('userType')
        telephone = request.POST.get('telephone', '')
        adresse = request.POST.get('adresse', '')
        boutique_nom = request.POST.get('boutique_nom', '')
        adresse_boutique = request.POST.get('adresse_boutique', '')
        role = request.POST.get('role', 'admin')
        zone_de_livraison = request.POST.get('zone_de_livraison', '')

        if Utilisateur.objects.filter(email=email).exists():
            messages.error(request, 'Cet email est déjà utilisé.')
            return render(request, 'register.html')

        utilisateur = Utilisateur(
            nom=nom,
            email=email,
            motDePasse=make_password(mot_de_passe)
        )
        utilisateur.save()

        # Création selon type
        if userType == 'client':
            Client.objects.create(utilisateur=utilisateur, adresse=adresse, telephone=telephone)
        elif userType == 'commercant':
            Commercant.objects.create(utilisateur=utilisateur, boutique_nom=boutique_nom, adresse_boutique=adresse_boutique)
        elif userType == 'administrateur':
            Administrateur.objects.create(utilisateur=utilisateur, role=role)
        elif userType == 'livreur':
            Livreur.objects.create(utilisateur=utilisateur, zone_de_livraison=zone_de_livraison, telephone=telephone)
        else:
            messages.error(request, 'Type d’utilisateur invalide.')
            return render(request, 'register.html')

        # Génération du token
        #tokens = get_tokens_for_user(utilisateur)
        #print("Tokens générés :", tokens)
        return redirect('/connexion')

    return render(request, "register.html")

def connexion(request):
    print('test')
    if request.method == 'POST':
        email = request.POST.get('email')
        mot_de_passe = request.POST.get('password')

        try:
            utilisateur = Utilisateur.objects.get(email=email)
        except Utilisateur.DoesNotExist:
            messages.error(request, 'Email ou mot de passe incorrect.')
            return render(request, 'register.html')

        if check_password(mot_de_passe, utilisateur.motDePasse):

            role = get_user_role(utilisateur)
            
            request.session['user_id'] = utilisateur.id
            request.session['nom'] = utilisateur.nom
            request.session['email'] = utilisateur.email
            request.session['role'] = get_user_role(utilisateur)

            messages.success(request, "Connexion réussie !")
            print("Rôle de l'utilisateur connecté :", role)
            if role == "client":
                return redirect('/Dashboard_client/')
            if role == "commercant":
                return redirect('/Dashboard_vendeur/')
            #if role in ["admin", "superadmin"]:
            #    return redirect('/administrateur/dashboard/')
            if role == "livreur":
                return redirect('/Dashboard_Livreur/')

            return redirect('inscription')  

        else:
            messages.error(request, 'Email ou mot de passe incorrect.')
            return render(request, 'login.html')


def get_user_role(utilisateur):
    if Client.objects.filter(utilisateur=utilisateur).exists():
        return "client"
    if Commercant.objects.filter(utilisateur=utilisateur).exists():
        return "commercant"
    if Administrateur.objects.filter(utilisateur=utilisateur).exists():
        admin = Administrateur.objects.get(utilisateur=utilisateur)
        return admin.role
    if Livreur.objects.filter(utilisateur=utilisateur).exists():
        return "livreur"
    return "inconnu"




def mot_de_passe_oublie(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            utilisateur = Utilisateur.objects.get(email=email)
        except Utilisateur.DoesNotExist:
            return render(request, 'password_reset_request.html', {'error': "Email non trouvé."})

        # Générer un code à 6 chiffres
        code = random.randint(100000, 999999)
        request.session['reset_code'] = code
        request.session['reset_user_id'] = utilisateur.id

        # Envoyer l'e-mail
        send_mail(
            subject="Réinitialisation de mot de passe",
            message=f"Votre code de réinitialisation est : {code}",
            from_email="no-reply@monapp.com",
            recipient_list=[utilisateur.email],
        )
        return redirect('verifier_code')
    
    return render(request, 'password_reset_request.html')

def verifier_code(request):
    if request.method == 'POST':
        code_saisi = request.POST.get('code')
        if str(code_saisi) == str(request.session.get('reset_code')):
            return redirect('reinitialiser_mdp')
        else:
            return render(request, 'verify_code.html', {'error': "Code incorrect."})

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

        request.session.pop('reset_code', None)
        request.session.pop('reset_user_id', None)

        return redirect('login')  

    return render(request, 'reset_password.html')

def mwp(request):
    return render(request,'password_reset_request.html')

def modifier_profil(request):
    utilisateur = get_object_or_404(Utilisateur, email=request.session.get('email'))
    errors = {}
    
    client = None
    commercant = None
    livreur = None
    administrateur = None
    
    try:
        client = Client.objects.get(utilisateur=utilisateur)
    except Client.DoesNotExist:
        pass
        
    try:
        commercant = Commercant.objects.get(utilisateur=utilisateur)
    except Commercant.DoesNotExist:
        pass
        
    try:
        livreur = Livreur.objects.get(utilisateur=utilisateur)
    except Livreur.DoesNotExist:
        pass
        
    try:
        administrateur = Administrateur.objects.get(utilisateur=utilisateur)
    except Administrateur.DoesNotExist:
        pass

    if request.method == 'POST':
        # Récupération des données du formulaire
        nom = request.POST.get('nom')
        email = request.POST.get('email')
        image = request.FILES.get('image')
        is_active = request.POST.get('is_active') == 'on'
        is_staff = request.POST.get('is_staff') == 'on'
        
        # Validation des données de base
        if not nom:
            errors['nom'] = ['Le nom est obligatoire']
        if not email:
            errors['email'] = ['L\'email est obligatoire']
        
        # Validation des données spécifiques
        if client:
            adresse = request.POST.get('adresse')
            telephone = request.POST.get('telephone')
            if not adresse:
                errors['adresse'] = ['L\'adresse est obligatoire pour un client']
            if not telephone:
                errors['telephone'] = ['Le téléphone est obligatoire pour un client']
                
        if livreur:
            zone_de_livraison = request.POST.get('zone_de_livraison')
            if not zone_de_livraison:
                errors['zone_de_livraison'] = ['La zone de livraison est obligatoire pour un livreur']
        
        if not errors:
            try:
                utilisateur.nom = nom
                utilisateur.email = email
                if image:
                    utilisateur.image = image
                
                if administrateur or request.user.is_superuser:
                    utilisateur.is_active = is_active
                    utilisateur.is_staff = is_staff
                
                utilisateur.save()
                
                if client:
                    client.adresse = request.POST.get('adresse', '')
                    client.telephone = request.POST.get('telephone', '')
                    client.save()
                    
                elif commercant:
                    commercant.boutique_nom = request.POST.get('boutique_nom', '')
                    commercant.adresse_boutique = request.POST.get('adresse_boutique', '')
                    commercant.save()
                    
                elif livreur:
                    livreur.zone_de_livraison = request.POST.get('zone_de_livraison', '')
                    livreur.telephone = request.POST.get('telephone_livreur', '')
                    livreur.save()
                    
                elif administrateur and request.user.is_superuser:
                    role = request.POST.get('role', 'admin')
                    administrateur.role = role
                    administrateur.save()
                
                messages.success(request, 'Votre profil a été mis à jour avec succès!')
                return redirect('call_profil')
                
            except Exception as e:
                messages.error(request, f'Une erreur est survenue: {str(e)}')
        else:
            for field, error_list in errors.items():
                for error in error_list:
                    messages.error(request, f"{field}: {error}")

    context = {
        'utilisateur': utilisateur,
        'client': client,
        'commercant': commercant,
        'livreur': livreur,
        'administrateur': administrateur,
        'errors': errors,
    }
    return render(request, 'modifier_profil.html', context)




#


#Un message de {{name}} a été reçu. Veuillez répondre dès que possible.
#👤
	
#inscription reussi :
#email utilisateur : {{user_email}}
#mot de passe : {{user_password}}

#email envoyer depuis : {{from_email}}
#email destinataire {{to_email}}
#{{temps}}


# views.py