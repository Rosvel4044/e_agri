from django.db import models

# Create your models here.
from django.db import models


from django.contrib.auth.models import AbstractUser

from django.db import models
from django.contrib.auth.models import AbstractUser

# =========================
# UTILISATEUR (Client & Vendeur)
# =========================
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class Utilisateur(AbstractUser):
    ROLE_CHOICES = (
        ('VENDEUR', 'Vendeur'),
        ('CLIENT', 'Client'),
    )

    # Champs d'identité
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    telephone = models.CharField(max_length=20, blank=True, null=True)

    # Spécifique vendeur
    nom_boutique = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    # ✅ FIX DU PROBLÈME
    groups = models.ManyToManyField(
        Group,
        related_name='agri_market_users',
        blank=True
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='agri_market_users_permissions',
        blank=True
    )

    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    def save(self, *args, **kwargs):
        if self.role != 'VENDEUR':
            self.nom_boutique = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.role})"


# =========================
# CATEGORIE
# =========================
class Categorie(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nom


# =========================
# PRODUIT
# =========================
class Produit(models.Model):
    vendeur = models.ForeignKey(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name='produits',
        limit_choices_to={'role': 'VENDEUR'}
    )
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE, related_name='produits')

    nom = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    quantite = models.PositiveIntegerField()
    #image = models.ImageField(upload_to='produits/', blank=True, null=True)
    date_ajout = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom


# =========================
# COMMANDE (Panier inclus)
# =========================
class Commande(models.Model):
    STATUT_CHOICES = (
        ('PANIER', 'Panier'),
        ('EN_ATTENTE', 'En attente'),
        ('PAYEE', 'Payée'),
        ('EXPEDIEE', 'Expédiée'),
        ('LIVREE', 'Livrée'),
        ('ANNULEE', 'Annulée'),
    )

    client = models.ForeignKey(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name='commandes',
        limit_choices_to={'role': 'CLIENT'}
    )
    statut = models.CharField(max_length=30, choices=STATUT_CHOICES, default='PANIER')
    montant_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date_commande = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commande #{self.id} - {self.client.username}"


# =========================
# LIGNE DE COMMANDE
# =========================
class LigneCommande(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('commande', 'produit')

    def __str__(self):
        return f"{self.quantite} x {self.produit.nom}"


# =========================
# PAIEMENT
# =========================
class Paiement(models.Model):
    MODE_PAIEMENT_CHOICES = (
        ('MOBILE_MONEY', 'Mobile Money'),
        ('CARTE', 'Carte bancaire'),
        ('ESPECES', 'Espèces'),
    )

    STATUT_CHOICES = (
        ('EN_ATTENTE', 'En attente'),
        ('REUSSI', 'Réussi'),
        ('ECHEC', 'Échec'),
    )

    reference = models.CharField(max_length=100, unique=True)
    commande = models.OneToOneField(Commande, on_delete=models.CASCADE, related_name='paiement')
    client = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    mode_paiement = models.CharField(max_length=30, choices=MODE_PAIEMENT_CHOICES)
    statut = models.CharField(max_length=30, choices=STATUT_CHOICES, default='EN_ATTENTE')
    date_paiement = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Paiement {self.reference}"

date_paiement = models.DateTimeField(auto_now_add=True)

def __str__(self):
    return f"Paiement {self.reference}"
