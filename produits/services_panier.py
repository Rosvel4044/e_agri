"""
Services pour la gestion du panier et des commandes
Auteur: Franck
"""

from django.db import transaction
from django.core.exceptions import ValidationError
from decimal import Decimal
from .models import Commande, LigneCommande, Produit, Utilisateur


class ServicePanier:
    """Service pour gérer le panier d'achat"""
    
    @staticmethod
    def obtenir_ou_creer_panier(client_id):
        """
        Obtenir le panier actif d'un client ou en créer un nouveau
        """
        try:
            client = Utilisateur.objects.get(id=client_id, role='CLIENT')
        except Utilisateur.DoesNotExist:
            raise ValidationError("Client introuvable")
        
        # Chercher un panier existant
        panier = Commande.objects.filter(
            client=client,
            statut='PANIER'
        ).first()
        
        # Créer un nouveau panier si nécessaire
        if not panier:
            panier = Commande.objects.create(
                client=client,
                statut='PANIER',
                montant_total=Decimal('0')
            )
        
        return panier
    
    @staticmethod
    @transaction.atomic
    def ajouter_au_panier(client_id, produit_id, quantite=1):
        """
        Ajouter un produit au panier
        """
        # Obtenir le panier
        panier = ServicePanier.obtenir_ou_creer_panier(client_id)
        
        # Vérifier le produit
        try:
            produit = Produit.objects.select_for_update().get(id=produit_id)
        except Produit.DoesNotExist:
            raise ValidationError("Produit introuvable")
        
        # Vérifier le stock
        if produit.quantite < quantite:
            raise ValidationError(f"Stock insuffisant. Disponible: {produit.quantite}")
        
        # Chercher si le produit est déjà dans le panier
        ligne_existante = LigneCommande.objects.filter(
            commande=panier,
            produit=produit
        ).first()
        
        if ligne_existante:
            # Mettre à jour la quantité
            nouvelle_quantite = ligne_existante.quantite + quantite
            
            if nouvelle_quantite > produit.quantite:
                raise ValidationError(f"Stock insuffisant. Disponible: {produit.quantite}")
            
            ligne_existante.quantite = nouvelle_quantite
            ligne_existante.save()
            ligne = ligne_existante
        else:
            # Créer une nouvelle ligne
            ligne = LigneCommande.objects.create(
                commande=panier,
                produit=produit,
                quantite=quantite,
                prix_unitaire=produit.prix
            )
        
        # Recalculer le montant total
        ServicePanier._recalculer_montant(panier)
        
        return ligne
    
    @staticmethod
    @transaction.atomic
    def modifier_quantite(client_id, ligne_id, nouvelle_quantite):
        """
        Modifier la quantité d'un article dans le panier
        """
        panier = ServicePanier.obtenir_ou_creer_panier(client_id)
        
        try:
            ligne = LigneCommande.objects.select_related('produit').get(
                id=ligne_id,
                commande=panier
            )
        except LigneCommande.DoesNotExist:
            raise ValidationError("Article introuvable dans le panier")
        
        if nouvelle_quantite <= 0:
            ligne.delete()
        else:
            if nouvelle_quantite > ligne.produit.quantite:
                raise ValidationError(f"Stock insuffisant. Disponible: {ligne.produit.quantite}")
            
            ligne.quantite = nouvelle_quantite
            ligne.save()
        
        ServicePanier._recalculer_montant(panier)
    
    @staticmethod
    @transaction.atomic
    def retirer_du_panier(client_id, ligne_id):
        """
        Retirer un produit du panier
        """
        panier = ServicePanier.obtenir_ou_creer_panier(client_id)
        
        try:
            ligne = LigneCommande.objects.get(id=ligne_id, commande=panier)
            ligne.delete()
        except LigneCommande.DoesNotExist:
            raise ValidationError("Article introuvable dans le panier")
        
        ServicePanier._recalculer_montant(panier)
    
    @staticmethod
    def vider_panier(client_id):
        """Vider complètement le panier"""
        panier = ServicePanier.obtenir_ou_creer_panier(client_id)
        panier.lignes.all().delete()
        panier.montant_total = Decimal('0')
        panier.save()
    
    @staticmethod
    def obtenir_panier_avec_details(client_id):
        """
        Obtenir le panier avec tous les détails
        """
        panier = ServicePanier.obtenir_ou_creer_panier(client_id)
        
        lignes = panier.lignes.select_related('produit', 'produit__vendeur').all()
        
        # Grouper par vendeur
        vendeurs_dict = {}
        for ligne in lignes:
            vendeur_id = ligne.produit.vendeur.id
            if vendeur_id not in vendeurs_dict:
                vendeurs_dict[vendeur_id] = {
                    'vendeur': ligne.produit.vendeur,
                    'lignes': [],
                    'sous_total': Decimal('0')
                }
            
            vendeurs_dict[vendeur_id]['lignes'].append(ligne)
            vendeurs_dict[vendeur_id]['sous_total'] += ligne.prix_unitaire * ligne.quantite
        
        return {
            'panier': panier,
            'lignes': lignes,
            'vendeurs': list(vendeurs_dict.values()),
            'nombre_articles': lignes.count(),
            'montant_total': panier.montant_total
        }
    
    @staticmethod
    @transaction.atomic
    def valider_commande(client_id, mode_retrait='LIVRAISON', adresse_livraison=''):
        """
        Transformer le panier en commande validée
        """
        panier = ServicePanier.obtenir_ou_creer_panier(client_id)
        
        if not panier.lignes.exists():
            raise ValidationError("Le panier est vide")
        
        # Vérifier les stocks pour tous les produits
        for ligne in panier.lignes.select_related('produit').select_for_update():
            if ligne.produit.quantite < ligne.quantite:
                raise ValidationError(
                    f"Stock insuffisant pour {ligne.produit.nom}. "
                    f"Disponible: {ligne.produit.quantite}"
                )
        
        # Changer le statut
        panier.statut = 'EN_ATTENTE'
        panier.save()
        
        # Créer des notifications pour les vendeurs
        ServicePanier._notifier_vendeurs(panier)
        
        return panier
    
    @staticmethod
    def _recalculer_montant(panier):
        """Recalculer le montant total du panier"""
        total = Decimal('0')
        for ligne in panier.lignes.all():
            total += ligne.prix_unitaire * ligne.quantite
        
        panier.montant_total = total
        panier.save()
    
    @staticmethod
    def _notifier_vendeurs(commande):
        """
        Créer des notifications pour les vendeurs concernés
        """
        from collections import defaultdict
        
        # Grouper les lignes par vendeur
        vendeurs_lignes = defaultdict(list)
        for ligne in commande.lignes.select_related('produit__vendeur'):
            vendeurs_lignes[ligne.produit.vendeur].append(ligne)
        
        # Pour chaque vendeur, on pourrait envoyer un email ici
        # Pour l'instant on laisse juste la commande visible dans leur interface
        pass
