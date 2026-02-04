
# agri_markets/urls.py

from django.urls import path
from . import views

app_name = 'agri_market'

# urlpatterns = [
#     path('inscription/', views.inscription, name='inscription'),
#     path('connexion/',   views.connexion,   name='connexion'),
#     path('acceuil', views.acceuil, name='acceuil'),
# ]



"""
Configuration des URLs pour la gestion des produits
"""

from django.urls import path
from . import views

urlpatterns = [
    # Page d'accueil
    path('', views.home, name='home'),
    
    # Authentification
    path('connexion/', views.connexion, name='connexion'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path('inscription/', views.inscription, name='inscription'),
    
    
    # URLs publiques
    path('liste', views.liste_produits, name='liste_produits'),
    path('produit/<int:produit_id>/', views.detail_produit, name='detail_produit'),
    
        # URLs client - Panier
    path('panier/', views.voir_panier, name='voir_panier'),
    path('panier/ajouter/<int:produit_id>/', views.ajouter_au_panier, name='ajouter_au_panier'),
    path('panier/modifier/<int:ligne_id>/', views.modifier_quantite_panier, name='modifier_quantite_panier'),
    path('panier/retirer/<int:ligne_id>/', views.retirer_du_panier, name='retirer_du_panier'),
    path('panier/vider/', views.vider_panier, name='vider_panier'),
    path('panier/valider/', views.valider_commande, name='valider_commande'),
    path('mes-commandes/', views.mes_commandes, name='mes_commandes'),
    
    # URLs vendeur
    path('vendeur/mes-produits/', views.mes_produits, name='mes_produits'),
    path('vendeur/ajouter-produit/', views.ajouter_produit, name='ajouter_produit'),
    path('vendeur/modifier-produit/<int:produit_id>/', views.modifier_produit, name='modifier_produit'),
    path('vendeur/supprimer-produit/<int:produit_id>/', views.supprimer_produit, name='supprimer_produit'),
    # URLs vendeur - Commandes
    path('vendeur/commandes/', views.commandes_vendeur, name='commandes_vendeur'),
    path('vendeur/commande/statut/<int:commande_id>/', views.changer_statut_commande, name='changer_statut_commande'),
    
     # Dashboard admin
    path('admin-dashboard/', views.dashboard_admin, name='dashboard_admin'),
    
    # API AJAX (optionnel)
    path('api/ajuster-stock/<int:produit_id>/', views.ajuster_stock_ajax, name='ajuster_stock_ajax'),
]

