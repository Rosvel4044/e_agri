from django.contrib import admin

# Register your models here.

from django.contrib import admin
"""
Configuration de l'interface d'administration Django
"""


from .models import Utilisateur, Categorie, Produit, Commande, LigneCommande, Paiement


@admin.register(Utilisateur)
class UtilisateurAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'first_name', 'last_name', 'nom_boutique')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'nom_boutique')
    ordering = ('-date_joined',)


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'description')
    search_fields = ('nom',)
    ordering = ('nom',)


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('nom', 'vendeur', 'categorie', 'prix', 'quantite', 'date_ajout')
    list_filter = ('categorie', 'date_ajout')
    search_fields = ('nom', 'description', 'vendeur__username')
    readonly_fields = ('date_ajout',)
    ordering = ('-date_ajout',)
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'description', 'categorie')
        }),
        ('Vendeur', {
            'fields': ('vendeur',)
        }),
        ('Prix et stock', {
            'fields': ('prix', 'quantite')
        }),
        ('Dates', {
            'fields': ('date_ajout',)
        }),
    )


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'statut', 'montant_total', 'date_commande')
    list_filter = ('statut', 'date_commande')
    search_fields = ('client__username', 'client__email')
    readonly_fields = ('date_commande',)
    ordering = ('-date_commande',)


@admin.register(LigneCommande)
class LigneCommandeAdmin(admin.ModelAdmin):
    list_display = ('commande', 'produit', 'quantite', 'prix_unitaire')
    search_fields = ('produit__nom', 'commande__client__username')


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ('reference', 'commande', 'client', 'montant', 'mode_paiement', 'statut', 'date_paiement')
    list_filter = ('statut', 'mode_paiement', 'date_paiement')
    search_fields = ('reference', 'client__username')
    readonly_fields = ('date_paiement',)
    ordering = ('-date_paiement',)


# Personnalisation de l'interface admin
admin.site.site_header = "Administration e_agri"
admin.site.site_title = "e_agri Admin"
admin.site.index_title = "Gestion de la plateforme agricole"

# Register your models here.
#from django.contrib import admin







