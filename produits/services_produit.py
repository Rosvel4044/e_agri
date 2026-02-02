"""
Services métier pour la gestion des produits agricoles
Auteur: Pavel
"""

from django.db import transaction
from django.core.exceptions import ValidationError, PermissionDenied
from .models import Produit, Categorie, Utilisateur


class ServiceProduit:
    """
    Service pour gérer toutes les opérations liées aux produits
    """

    @staticmethod
    def creer_produit(vendeur_id, nom, prix, quantite, categorie_id, description=""):
        """
        Créer un nouveau produit
        
        Args:
            vendeur_id: ID de l'utilisateur vendeur
            nom: Nom du produit
            prix: Prix unitaire
            quantite: Quantité en stock
            categorie_id: ID de la catégorie
            description: Description du produit (optionnel)
            
        Returns:
            Produit: Le produit créé
            
        Raises:
            ValidationError: Si les données sont invalides
            PermissionDenied: Si l'utilisateur n'est pas vendeur
        """
        try:
            # Vérifier que l'utilisateur est bien un vendeur
            vendeur = Utilisateur.objects.get(id=vendeur_id)
            if vendeur.role != 'VENDEUR':
                raise PermissionDenied("Seuls les vendeurs peuvent ajouter des produits")
            
            # Vérifier que la catégorie existe
            categorie = Categorie.objects.get(id=categorie_id)
            
            # Validation des données
            if prix <= 0:
                raise ValidationError("Le prix doit être supérieur à 0")
            
            if quantite < 0:
                raise ValidationError("La quantité ne peut pas être négative")
            
            # Création du produit
            produit = Produit.objects.create(
                vendeur=vendeur,
                categorie=categorie,
                nom=nom,
                description=description,
                prix=prix,
                quantite=quantite
            )
            
            return produit
            
        except Utilisateur.DoesNotExist:
            raise ValidationError("Vendeur introuvable")
        except Categorie.DoesNotExist:
            raise ValidationError("Catégorie introuvable")

    @staticmethod
    def modifier_produit(produit_id, vendeur_id, **kwargs):
        """
        Modifier un produit existant
        
        Args:
            produit_id: ID du produit à modifier
            vendeur_id: ID du vendeur (pour vérification)
            **kwargs: Champs à modifier (nom, prix, quantite, description, categorie_id)
            
        Returns:
            Produit: Le produit modifié
            
        Raises:
            ValidationError: Si les données sont invalides
            PermissionDenied: Si le vendeur n'est pas le propriétaire
        """
        try:
            produit = Produit.objects.get(id=produit_id)
            
            # Vérifier que c'est bien le vendeur du produit
            if produit.vendeur.id != vendeur_id:
                raise PermissionDenied("Vous ne pouvez modifier que vos propres produits")
            
            # Mise à jour des champs
            if 'nom' in kwargs:
                produit.nom = kwargs['nom']
            
            if 'description' in kwargs:
                produit.description = kwargs['description']
            
            if 'prix' in kwargs:
                if kwargs['prix'] <= 0:
                    raise ValidationError("Le prix doit être supérieur à 0")
                produit.prix = kwargs['prix']
            
            if 'quantite' in kwargs:
                if kwargs['quantite'] < 0:
                    raise ValidationError("La quantité ne peut pas être négative")
                produit.quantite = kwargs['quantite']
            
            if 'categorie_id' in kwargs:
                categorie = Categorie.objects.get(id=kwargs['categorie_id'])
                produit.categorie = categorie
            
            produit.save()
            return produit
            
        except Produit.DoesNotExist:
            raise ValidationError("Produit introuvable")
        except Categorie.DoesNotExist:
            raise ValidationError("Catégorie introuvable")

    @staticmethod
    def supprimer_produit(produit_id, vendeur_id):
        """
        Supprimer un produit
        
        Args:
            produit_id: ID du produit à supprimer
            vendeur_id: ID du vendeur (pour vérification)
            
        Returns:
            bool: True si supprimé avec succès
            
        Raises:
            PermissionDenied: Si le vendeur n'est pas le propriétaire
        """
        try:
            produit = Produit.objects.get(id=produit_id)
            
            # Vérifier que c'est bien le vendeur du produit
            if produit.vendeur.id != vendeur_id:
                raise PermissionDenied("Vous ne pouvez supprimer que vos propres produits")
            
            produit.delete()
            return True
            
        except Produit.DoesNotExist:
            raise ValidationError("Produit introuvable")

    @staticmethod
    def obtenir_produit(produit_id):
        """
        Obtenir les détails d'un produit
        
        Args:
            produit_id: ID du produit
            
        Returns:
            Produit: Le produit demandé
        """
        try:
            return Produit.objects.select_related('vendeur', 'categorie').get(id=produit_id)
        except Produit.DoesNotExist:
            raise ValidationError("Produit introuvable")

    @staticmethod
    def lister_produits_vendeur(vendeur_id):
        """
        Lister tous les produits d'un vendeur
        
        Args:
            vendeur_id: ID du vendeur
            
        Returns:
            QuerySet: Liste des produits du vendeur
        """
        return Produit.objects.filter(
            vendeur_id=vendeur_id
        ).select_related('categorie').order_by('-date_ajout')

    @staticmethod
    def lister_tous_produits():
        """
        Lister tous les produits disponibles (quantité > 0)
        
        Returns:
            QuerySet: Liste de tous les produits disponibles
        """
        return Produit.objects.filter(
            quantite__gt=0
        ).select_related('vendeur', 'categorie').order_by('-date_ajout')

    @staticmethod
    def rechercher_produits(terme_recherche):
        """
        Rechercher des produits par nom ou description
        
        Args:
            terme_recherche: Terme à rechercher
            
        Returns:
            QuerySet: Produits correspondants
        """
        return Produit.objects.filter(
            nom__icontains=terme_recherche
        ).select_related('vendeur', 'categorie') | Produit.objects.filter(
            description__icontains=terme_recherche
        ).select_related('vendeur', 'categorie')

    @staticmethod
    def filtrer_par_categorie(categorie_id):
        """
        Filtrer les produits par catégorie
        
        Args:
            categorie_id: ID de la catégorie
            
        Returns:
            QuerySet: Produits de la catégorie
        """
        return Produit.objects.filter(
            categorie_id=categorie_id,
            quantite__gt=0
        ).select_related('vendeur', 'categorie').order_by('-date_ajout')

    @staticmethod
    @transaction.atomic
    def ajuster_stock(produit_id, quantite_delta):
        """
        Ajuster le stock d'un produit
        
        Args:
            produit_id: ID du produit
            quantite_delta: Quantité à ajouter (positif) ou retirer (négatif)
            
        Returns:
            Produit: Le produit avec stock mis à jour
            
        Raises:
            ValidationError: Si stock insuffisant
        """
        try:
            produit = Produit.objects.select_for_update().get(id=produit_id)
            
            nouvelle_quantite = produit.quantite + quantite_delta
            
            if nouvelle_quantite < 0:
                raise ValidationError(f"Stock insuffisant. Disponible: {produit.quantite}")
            
            produit.quantite = nouvelle_quantite
            produit.save()
            
            return produit
            
        except Produit.DoesNotExist:
            raise ValidationError("Produit introuvable")


class ServiceCategorie:
    """
    Service pour gérer les catégories de produits
    """

    @staticmethod
    def creer_categorie(nom, description=""):
        """
        Créer une nouvelle catégorie
        
        Args:
            nom: Nom de la catégorie
            description: Description (optionnel)
            
        Returns:
            Categorie: La catégorie créée
        """
        categorie = Categorie.objects.create(
            nom=nom,
            description=description
        )
        return categorie

    @staticmethod
    def lister_categories():
        """
        Lister toutes les catégories
        
        Returns:
            QuerySet: Toutes les catégories
        """
        return Categorie.objects.all().order_by('nom')

    @staticmethod
    def obtenir_categorie(categorie_id):
        """
        Obtenir une catégorie par son ID
        
        Args:
            categorie_id: ID de la catégorie
            
        Returns:
            Categorie: La catégorie demandée
        """
        try:
            return Categorie.objects.get(id=categorie_id)
        except Categorie.DoesNotExist:
            raise ValidationError("Catégorie introuvable")
