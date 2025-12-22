import uuid
import random
import time

def traiter_paiement_mobile(numero, montant, reseau):
    """
    Simule une requête vers l'API Orange Money ou MTN Mobile Money.
    Retourne (succes: bool, reference_transaction: str, message: str)
    """
    # Ici, vous utiliseriez 'requests' pour appeler l'API réelle
    # Ex: response = requests.post('https://api.orange.com/...', data={...})
    
    print(f"Traitement paiement {reseau} pour {montant} FCFA sur le {numero}...")
    time.sleep(2) # Simulation de latence réseau
    
    # Simulation : 90% de chance de succès
    succes = random.random() > 0.1
    ref = str(uuid.uuid4())[:8].upper()
    
    if succes:
        return True, ref, "Transaction approuvée par l'opérateur."
    else:
        return False, None, "Solde insuffisant ou délai dépassé."
    

def verifier_statut_transaction(reference):
    """
    Simule la vérification du statut d'une transaction via l'API.
    Retourne (succes: bool, statut: str)
    """
    print(f"Vérification du statut pour la transaction {reference}...")
    time.sleep(1) # Simulation de latence réseau
    
    # Simulation : 95% de chance que la transaction soit réussie
    succes = random.random() > 0.05
    
    if succes:
        return True, "Transaction réussie."
    else:
        return False, "Transaction échouée ou en attente."
    

# Autres services liés aux paiements mobiles peuvent être ajoutés ici

#calculer les frais de livraison en fonction de la distance on peut utiliser un service externe comme google maps
def calculer_frais_livraison(distance_km):
    """
    Calcule les frais de livraison en fonction de la distance en kilomètres.
    """
    tarif_base = 500  # Tarif de base en FCFA
    tarif_par_km = 200  # Tarif par kilomètre en FCFA
    
    frais = tarif_base + (tarif_par_km * distance_km)
    return frais


#Les frais ou béné fices retenu par la plateforme sur chaque transaction
def calculer_frais_plateforme(montant_transaction):
    """
    Calcule les frais retenus par la plateforme sur une transaction donnée.
    """
    pourcentage_frais = 0.05  # 5% de frais de plateforme
    frais = montant_transaction * pourcentage_frais
    return frais    

#Envoyer l'argent dans le compte Orange Money ou MTN Mobile Money de la plateforme
def envoyer_argent_mobile(numero, montant, reseau):
    """
    Simule l'envoi d'argent vers un compte Orange Money ou MTN Mobile Money.
    Retourne (succes: bool, reference_transaction: str, message: str)
    """
    print(f"Envoi de {montant} FCFA vers le {numero} via {reseau}...")
    time.sleep(2) # Simulation de latence réseau
    
    # Simulation : 90% de chance de succès
    succes = random.random() > 0.1
    ref = str(uuid.uuid4())[:8].upper()
    
    if succes:
        return True, ref, "Envoi réussi."
    else:
        return False, None, "Échec de l'envoi. Veuillez réessayer."