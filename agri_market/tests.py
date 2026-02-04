from django.test import TestCase

# Create your tests here.

from django.test import TestCase

# Create your tests here.

"""
Tests unitaires pour la gestion des produits
Auteur: Pavel (responsable tests)
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError, PermissionDenied
from decimal import Decimal

from .models import Utilisateur, Categorie, Produit
from .services_produit import ServiceProduit, ServiceCategorie


class ServiceProduitTestCase(TestCase):
    """Tests pour le service de gestion des produits"""
    
    def setUp(self):
        """Préparation des données de test"""
        # Créer un vendeur
        self.vendeur = Utilisateur.objects.create_user(
            username='vendeur_test',
            email='vendeur@test.com',
            password='password123',
            first_name='Jean',
            last_name='Dupont',
            role='VENDEUR',
            nom_boutique='Boutique Test'
        )
        
        # Créer un client
        self.client_user = Utilisateur.objects.create_user(
            username='client_test',
            email='client@test.com',
            password='password123',
            first_name='Marie',
            last_name='Martin',
            role='CLIENT'
        )
        
        # Créer une catégorie
        self.categorie = Categorie.objects.create(
            nom='Légumes',
            description='Légumes frais'
        )
    
    def test_creer_produit_succes(self):
        """Test de création d'un produit valide"""
        produit = ServiceProduit.creer_produit(
            vendeur_id=self.vendeur.id,
            nom='Tomates',
            prix=500,
            quantite=100,
            categorie_id=self.categorie.id,
            description='Tomates fraîches'
        )
        
        self.assertIsNotNone(produit)
        self.assertEqual(produit.nom, 'Tomates')
        self.assertEqual(produit.prix, Decimal('500'))
        self.assertEqual(produit.quantite, 100)
        self.assertEqual(produit.vendeur, self.vendeur)
    
    def test_creer_produit_client_interdit(self):
        """Test qu'un client ne peut pas créer de produit"""
        with self.assertRaises(PermissionDenied):
            ServiceProduit.creer_produit(
                vendeur_id=self.client_user.id,
                nom='Tomates',
                prix=500,
                quantite=100,
                categorie_id=self.categorie.id
            )
    
    def test_creer_produit_prix_invalide(self):
        """Test avec un prix négatif"""
        with self.assertRaises(ValidationError):
            ServiceProduit.creer_produit(
                vendeur_id=self.vendeur.id,
                nom='Tomates',
                prix=-100,
                quantite=50,
                categorie_id=self.categorie.id
            )
    
    def test_modifier_produit_succes(self):
        """Test de modification d'un produit"""
        # Créer un produit
        produit = ServiceProduit.creer_produit(
            vendeur_id=self.vendeur.id,
            nom='Tomates',
            prix=500,
            quantite=100,
            categorie_id=self.categorie.id
        )
        
        # Modifier le produit
        produit_modifie = ServiceProduit.modifier_produit(
            produit_id=produit.id,
            vendeur_id=self.vendeur.id,
            nom='Tomates Bio',
            prix=700
        )
        
        self.assertEqual(produit_modifie.nom, 'Tomates Bio')
        self.assertEqual(produit_modifie.prix, Decimal('700'))
    
    def test_modifier_produit_autre_vendeur(self):
        """Test qu'un vendeur ne peut pas modifier le produit d'un autre"""
        # Créer un autre vendeur
        autre_vendeur = Utilisateur.objects.create_user(
            username='autre_vendeur',
            email='autre@test.com',
            password='password123',
            first_name='Paul',
            last_name='Durand',
            role='VENDEUR'
        )
        
        # Créer un produit
        produit = ServiceProduit.creer_produit(
            vendeur_id=self.vendeur.id,
            nom='Tomates',
            prix=500,
            quantite=100,
            categorie_id=self.categorie.id
        )
        
        # Tenter de modifier avec un autre vendeur
        with self.assertRaises(PermissionDenied):
            ServiceProduit.modifier_produit(
                produit_id=produit.id,
                vendeur_id=autre_vendeur.id,
                nom='Tomates Bio'
            )
    
    def test_supprimer_produit_succes(self):
        """Test de suppression d'un produit"""
        produit = ServiceProduit.creer_produit(
            vendeur_id=self.vendeur.id,
            nom='Tomates',
            prix=500,
            quantite=100,
            categorie_id=self.categorie.id
        )
        
        resultat = ServiceProduit.supprimer_produit(
            produit_id=produit.id,
            vendeur_id=self.vendeur.id
        )
        
        self.assertTrue(resultat)
        self.assertEqual(Produit.objects.filter(id=produit.id).count(), 0)
    
    def test_ajuster_stock_succes(self):
        """Test d'ajustement du stock"""
        produit = ServiceProduit.creer_produit(
            vendeur_id=self.vendeur.id,
            nom='Tomates',
            prix=500,
            quantite=100,
            categorie_id=self.categorie.id
        )
        
        # Retirer 30 unités
        produit_mis_a_jour = ServiceProduit.ajuster_stock(
            produit_id=produit.id,
            quantite_delta=-30
        )
        
        self.assertEqual(produit_mis_a_jour.quantite, 70)
    
    def test_ajuster_stock_insuffisant(self):
        """Test avec un stock insuffisant"""
        produit = ServiceProduit.creer_produit(
            vendeur_id=self.vendeur.id,
            nom='Tomates',
            prix=500,
            quantite=10,
            categorie_id=self.categorie.id
        )
        
        with self.assertRaises(ValidationError):
            ServiceProduit.ajuster_stock(
                produit_id=produit.id,
                quantite_delta=-50
            )
    
    def test_rechercher_produits(self):
        """Test de recherche de produits"""
        ServiceProduit.creer_produit(
            vendeur_id=self.vendeur.id,
            nom='Tomates rouges',
            prix=500,
            quantite=100,
            categorie_id=self.categorie.id
        )
        
        ServiceProduit.creer_produit(
            vendeur_id=self.vendeur.id,
            nom='Carottes',
            prix=300,
            quantite=50,
            categorie_id=self.categorie.id
        )
        
        resultats = ServiceProduit.rechercher_produits('tomates')
        self.assertEqual(resultats.count(), 1)
        self.assertEqual(resultats.first().nom, 'Tomates rouges')


class VuesProduitsTestCase(TestCase):
    """Tests pour les vues de gestion des produits"""
    
    def setUp(self):
        """Préparation des données de test"""
        self.client = Client()
        
        self.vendeur = Utilisateur.objects.create_user(
            username='vendeur_test',
            email='vendeur@test.com',
            password='password123',
            first_name='Jean',
            last_name='Dupont',
            role='VENDEUR',
            nom_boutique='Boutique Test'
        )
        
        self.categorie = Categorie.objects.create(
            nom='Légumes',
            description='Légumes frais'
        )
    
    def test_liste_produits_accessible(self):
        """Test que la page liste produits est accessible"""
        response = self.client.get(reverse('liste_produits'))
        self.assertEqual(response.status_code, 200)
    
    def test_ajouter_produit_requiert_connexion(self):
        """Test que l'ajout de produit requiert une connexion"""
        response = self.client.get(reverse('ajouter_produit'))
        # Redirection vers login
        self.assertEqual(response.status_code, 302)
    
    def test_ajouter_produit_vendeur_connecte(self):
        """Test d'ajout de produit par un vendeur connecté"""
        self.client.login(username='vendeur_test', password='password123')
        
        response = self.client.post(reverse('ajouter_produit'), {
            'nom': 'Tomates',
            'prix': 500,
            'quantite': 100,
            'categorie': self.categorie.id,
            'description': 'Tomates fraîches'
        })
        
        # Vérifier la redirection après création
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Produit.objects.count(), 1)
    
    def test_mes_produits_vendeur_uniquement(self):
        """Test que seul un vendeur peut accéder à 'mes produits'"""
        client_user = Utilisateur.objects.create_user(
            username='client_test',
            email='client@test.com',
            password='password123',
            first_name='Marie',
            last_name='Martin',
            role='CLIENT'
        )
        
        self.client.login(username='client_test', password='password123')
        response = self.client.get(reverse('mes_produits'))
        
        # Redirection car non vendeur
        self.assertEqual(response.status_code, 302)


# Commande pour exécuter les tests
# python manage.py test agri_market
