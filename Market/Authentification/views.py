from django.shortcuts import render, redirect
import random
from django.contrib import messages
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

@csrf_exempt
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
        tokens = get_tokens_for_user(utilisateur)
        return render(request, 'login.html', {'tokens': tokens, 'user': utilisateur})

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
            request.session['role'] = get_user_role(utilisateur)

            messages.success(request, "Connexion réussie !")
            return render(request, 'login.html', {'utilisateur': utilisateur, 'role': role})
            #if role == "client":
            #    return redirect('/client/dashboard/')
            #if role == "commercant":
            #    return redirect('/commercant/dashboard/')
            #if role in ["admin", "superadmin"]:
            #    return redirect('/administrateur/dashboard/')
            #if role == "livreur":
            #    return redirect('/livreur/dashboard/')

            return redirect('home')  

        else:
            messages.error(request, 'Email ou mot de passe incorrect.')
            return render(request, 'login.html')


def get_user_role(utilisateur):
    if hasattr(utilisateur, 'client'):
        return "client"
    if hasattr(utilisateur, 'commercant'):
        return "commercant"
    if hasattr(utilisateur, 'administrateur'):
        return utilisateur.administrateur.role
    if hasattr(utilisateur, 'livreur'):
        return "livreur"
    return "inconnu"


#def envoyer_mot_de_passe(request):
#    message = ""
#
#    if request.method == 'POST':
#        email = request.POST.get('email')
#
#        try:
#            user = Etudiant.objects.get(email=email)
#
#            msg = EmailMessage()
#            msg['Subject'] = "Votre mot de passe"
#            msg['From'] = "{email}"
#            msg['To'] = "zikemstephane@gmail.com"
#            msg.set_content(f"Bonjour {email},\n\nVoici votre mot de passe : {password}")
#
#            # ⚠️ Désactivation de la vérification SSL — à ne pas utiliser en production
#            context = ssl._create_unverified_context()
#
#            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
#                smtp.login("zikemstephane@gmail.com", "znghyeokurdjdrea")
#                smtp.send_message(msg)
#
#            message = "Mot de passe envoyé avec succès."
#
#        except Etudiant.DoesNotExist:
#            message = "Aucun utilisateur avec cet e-mail."
#
#    return render(request, 'mdp oublie.html', {'message': message})


#Un message de {{name}} a été reçu. Veuillez répondre dès que possible.
#👤
	
#inscription reussi :
#email utilisateur : {{user_email}}
#mot de passe : {{user_password}}

#email envoyer depuis : {{from_email}}
#email destinataire {{to_email}}
#{{temps}}


# views.py
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

        # Supprimer les infos de session
        request.session.pop('reset_code', None)
        request.session.pop('reset_user_id', None)

        return redirect('login')  # Rediriger vers login après réinitialisation

    return render(request, 'reset_password.html')

def mwp(request):
    return render(request,'password_reset_request.html')