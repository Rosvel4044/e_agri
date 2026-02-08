# from django.shortcuts import render

# # Create your views here.

"""
Vues pour la gestion des produits et du panier
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError, PermissionDenied
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.contrib.admin.views.decorators import staff_member_required

from .models import Produit, Categorie, Utilisateur, Commande, LigneCommande
from .services_produit import ServiceProduit, ServiceCategorie
from .services_panier import ServicePanier
from django.views.decorators.csrf import csrf_exempt

# =========================
# PAGE D'ACCUEIL
# =========================

def home(request):
    """Page d'accueil du site"""
    return render(request, 'home.html')


# =========================
# AUTHENTIFICATION
# =========================

def connexion(request):
    """
    Vue de connexion sans formulaire Django.
    Accepte email OU username dans le champ 'email'.
    Gestion du paramètre ?next=
    Redirection intelligente selon le rôle de l'utilisateur.
    """
    if request.method == 'POST':
        # Récupération des données du formulaire
        identifiant = request.POST.get('email')  # champ nommé 'email' mais accepte username ou email
        password = request.POST.get('password')

        if not identifiant or not password:
            messages.error(request, "Veuillez remplir tous les champs.")
            return render(request, 'connexion.html')

        # Tenter l'authentification
        # On essaie d'abord avec username = identifiant
        user = authenticate(request, username=identifiant, password=password)

        # Si ça échoue et que c'est un email, on cherche l'utilisateur par email
        if user is None and '@' in identifiant:
            try:
                from agri_market.models import Utilisateur
                user_by_email = Utilisateur.objects.get(email__iexact=identifiant)
                user = authenticate(request, username=user_by_email.username, password=password)
            except Utilisateur.DoesNotExist:
                pass

        if user is not None:
            # Vérifier que le compte est actif
            if not user.is_active:
                messages.error(request, "Votre compte est désactivé. Contactez l'administrateur.")
                return render(request, 'connexion.html')

            # Connexion réussie
            login(request, user)
            messages.success(request, f"Bienvenue {user.get_full_name() or user.username} !")

            # Gestion du paramètre ?next= (sécurité contre open redirect)
            next_url = request.GET.get('next')
            if next_url and next_url.startswith('/'):
                # next_url valide → redirection vers la page demandée
                return redirect(next_url)
            
            # Sinon : redirection selon le rôle
            if user.role == 'VENDEUR':
                # Redirection vendeur (page d'ajout produit ou dashboard vendeur)
                return redirect('ajouter_produit')  # ou 'mes_produits' ou reverse('agri_market:mes_produits')
            else:
                # Redirection client (accueil ou catalogue)
                return redirect('home')  # ou 'liste_produits' selon ton choix

        else:
            messages.error(request, "Email / nom d'utilisateur ou mot de passe incorrect.")

    # GET ou échec → affichage de la page
    return render(request, 'connexion.html')
def deconnexion(request):
    """Déconnexion"""
    logout(request)
    messages.success(request, "Vous avez été déconnecté avec succès")
    return redirect('home')


def inscription(request):
    """Page d'inscription"""
    if request.method == 'POST':
        try:
            # Récupérer les données
            username = request.POST.get('username')
            email = request.POST.get('email')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            role = request.POST.get('role')
            telephone = request.POST.get('telephone', '')
            nom_boutique = request.POST.get('nom_boutique', '')
            
            # Validations
            if password1 != password2:
                messages.error(request, "Les mots de passe ne correspondent pas")
                return render(request, 'inscription.html')
            
            if Utilisateur.objects.filter(username=username).exists():
                messages.error(request, "Ce nom d'utilisateur existe déjà")
                return render(request, 'inscription.html')
            
            if Utilisateur.objects.filter(email=email).exists():
                messages.error(request, "Cet email est déjà utilisé")
                return render(request, 'inscription.html')
            
            if role == 'VENDEUR' and not nom_boutique:
                messages.error(request, "Le nom de la boutique est obligatoire pour les vendeurs")
                return render(request, 'inscription.html')
            
            # Créer l'utilisateur
            user = Utilisateur.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name,
                role=role,
                telephone=telephone,
                nom_boutique=nom_boutique if role == 'VENDEUR' else None
            )
            
            messages.success(request, "Compte créé avec succès ! Vous pouvez maintenant vous connecter.")
            return redirect('connexion')
            
        except Exception as e:
            messages.error(request, f"Erreur lors de la création du compte : {str(e)}")
    
    return render(request, 'inscription.html')


# =========================
# VUES PUBLIQUES (Catalogue)
# =========================

def liste_produits(request):
    """
    Afficher tous les produits disponibles (page publique)
    """
    # Recherche et filtrage
    terme_recherche = request.GET.get('recherche', '')
    categorie_id = request.GET.get('categorie', '')
    
    if terme_recherche:
        produits = ServiceProduit.rechercher_produits(terme_recherche)
    elif categorie_id:
        produits = ServiceProduit.filtrer_par_categorie(categorie_id)
    else:
        produits = ServiceProduit.lister_tous_produits()
    
    categories = ServiceCategorie.lister_categories()
    
    context = {
        'produits': produits,
        'categories': categories,
        'terme_recherche': terme_recherche,
        'categorie_selectionnee': categorie_id
    }
    
    return render(request, 'liste.html', context)


def detail_produit(request, produit_id):
    """
    Afficher les détails d'un produit
    """
    try:
        produit = ServiceProduit.obtenir_produit(produit_id)
        
        # Produits similaires (même catégorie)
        produits_similaires = Produit.objects.filter(
            categorie=produit.categorie
        ).exclude(id=produit_id)[:4]
        
        context = {
            'produit': produit,
            'produits_similaires': produits_similaires
        }
        
        return render(request, 'detail.html', context)
        
    except ValidationError as e:
        messages.error(request, str(e))
        return redirect('liste_produits')


# =========================
# VUES VENDEUR (Gestion)
# =========================

@login_required
def mes_produits(request):
    if request.user.role != 'VENDEUR':
        messages.error(request, "Accès réservé aux vendeurs")
        return redirect('agri_market:liste_produits')

    produits = ServiceProduit.lister_produits_vendeur(request.user.id)

    return render(request, 'mes_produits.html', {
        'produits': produits
    })

@login_required(login_url='/agri_market/connexion/')
def ajouter_produit(request):
    if request.user.role != 'VENDEUR':
        messages.error(request, "Accès réservé aux vendeurs")
        return redirect('agri_market:liste_produits')

    if request.method == 'POST':
        try:
            produit = ServiceProduit.creer_produit(
                vendeur_id=request.user.id,
                nom=request.POST.get('nom'),
                prix=float(request.POST.get('prix')),
                quantite=int(request.POST.get('quantite')),
                categorie_id=int(request.POST.get('categorie')),
                description=request.POST.get('description', '')
            )

            messages.success(request, "Produit ajouté avec succès")
            return redirect('agri_market:mes_produits')

        except Exception as e:
            messages.error(request, str(e))

    categories = ServiceCategorie.lister_categories()
    return render(request, 'ajouter_produit.html', {
        'categories': categories
    })

    if request.method == 'POST':
        try:
            # Récupérer les données du formulaire
            nom = request.POST.get('nom')
            description = request.POST.get('description', '')
            prix = float(request.POST.get('prix'))
            quantite = int(request.POST.get('quantite'))
            categorie_id = int(request.POST.get('categorie'))
            
            # Créer le produit via le service
            produit = ServiceProduit.creer_produit(
                vendeur_id=request.user.id,
                nom=nom,
                prix=prix,
                quantite=quantite,
                categorie_id=categorie_id,
                description=description
            )
            
            messages.success(request, f"Produit '{produit.nom}' ajouté avec succès !")
            return redirect('mes_produits')
            
        except (ValidationError, PermissionDenied) as e:
            messages.error(request, str(e))
        except ValueError:
            messages.error(request, "Veuillez vérifier les données saisies")
    
    # GET request ou erreur : afficher le formulaire
    categories = ServiceCategorie.lister_categories()
    
    context = {
        'categories': categories
    }
    
    return render(request, 'ajouter_produit.html', context)



@login_required
def modifier_produit(request, produit_id):
    if request.user.role != 'VENDEUR':
        messages.error(request, "Accès réservé aux vendeurs")
        return redirect('agri_market:liste_produits')

    produit = ServiceProduit.obtenir_produit(produit_id)

    if produit.vendeur.id != request.user.id:
        messages.error(request, "Produit non autorisé")
        return redirect('agri_market:mes_produits')

    if request.method == 'POST':
        try:
            ServiceProduit.modifier_produit(
                produit_id=produit_id,
                vendeur_id=request.user.id,
                nom=request.POST.get('nom'),
                prix=float(request.POST.get('prix')),
                quantite=int(request.POST.get('quantite')),
                categorie_id=int(request.POST.get('categorie')),
                description=request.POST.get('description', '')
            )
            messages.success(request, "Produit modifié")
            return redirect('agri_market:mes_produits')

        except Exception as e:
            messages.error(request, str(e))

    categories = ServiceCategorie.lister_categories()
    return render(request, 'modifier_produit.html', {
        'produit': produit,
        'categories': categories
    })

@login_required
#@require_POST
def supprimer_produit(request, produit_id):
    if request.user.role != 'VENDEUR':
        messages.error(request, "Accès refusé")
        return redirect('agri_market:liste_produits')

    ServiceProduit.supprimer_produit(
        produit_id=produit_id,
        vendeur_id=request.user.id
    )

    messages.success(request, "Produit supprimé")
    return redirect('agri_market:mes_produits')


# =========================
# GESTION DU PANIER
# =========================

@login_required
def voir_panier(request):
    """Afficher le panier du client"""
    if request.user.role != 'CLIENT':
        messages.error(request, "Seuls les clients peuvent avoir un panier")
        return redirect('liste_produits')
    
    try:
        details = ServicePanier.obtenir_panier_avec_details(request.user.id)
        
        context = {
            'panier': details['panier'],
            'lignes': details['lignes'],
            'vendeurs': details['vendeurs'],
            'nombre_articles': details['nombre_articles'],
            'montant_total': details['montant_total'],
        }
        
        return render(request, 'agri_market/panier/voir_panier.html', context)
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement du panier: {str(e)}")
        return redirect('liste_produits')


@login_required
def ajouter_au_panier(request, produit_id):
    """Ajouter un produit au panier"""
    from decimal import Decimal
    
    print(f"\n{'='*60}")
    print(f"🛒 REQUÊTE REÇUE!")
    print(f"   Méthode: {request.method}")
    print(f"   User: {request.user.username}")
    print(f"   Produit ID: {produit_id}")
    print(f"   POST data: {request.POST}")
    print(f"{'='*60}\n")
    
    # Vérifier la méthode
    if request.method != 'POST':
        messages.error(request, "Méthode non autorisée")
        return redirect('detail_produit', produit_id=produit_id)
    
    # Vérifier le rôle
    if request.user.role != 'CLIENT':
        messages.error(request, "Seuls les clients peuvent ajouter au panier")
        return redirect('detail_produit', produit_id=produit_id)
    
    try:
        # Récupérer le produit
        produit = Produit.objects.get(id=produit_id)
        print(f"✅ Produit trouvé: {produit.nom}")
        
        # Récupérer la quantité
        quantite = int(request.POST.get('quantite', 1))
        print(f"✅ Quantité: {quantite}")
        
        # Vérifier le stock
        if produit.quantite < quantite:
            messages.error(request, f"Stock insuffisant. Disponible: {produit.quantite}")
            return redirect('detail_produit', produit_id=produit_id)
        
        # Obtenir ou créer le panier
        panier, created = Commande.objects.get_or_create(
            client=request.user,
            statut='PANIER',
            defaults={'montant_total': Decimal('0')}
        )
        print(f"✅ Panier: ID={panier.id} (nouveau={created})")
        
        # Vérifier si le produit est déjà dans le panier
        ligne_existante = LigneCommande.objects.filter(
            commande=panier,
            produit=produit
        ).first()
        
        if ligne_existante:
            print(f"📝 Mise à jour ligne existante")
            ligne_existante.quantite += quantite
            ligne_existante.save()
            ligne = ligne_existante
        else:
            print(f"➕ Création nouvelle ligne")
            ligne = LigneCommande.objects.create(
                commande=panier,
                produit=produit,
                quantite=quantite,
                prix_unitaire=produit.prix
            )
        
        print(f"✅ Ligne sauvegardée: ID={ligne.id}")
        
        # Recalculer le total
        total = Decimal('0')
        for l in panier.lignes.all():
            total += l.prix_unitaire * l.quantite
        panier.montant_total = total
        panier.save()
        
        print(f"✅ Total recalculé: {total} FCFA")
        print(f"✅ SUCCÈS COMPLET!\n")
        
        messages.success(request, f"✅ {produit.nom} ajouté au panier !")
        return redirect('voir_panier')
        
    except Produit.DoesNotExist:
        print(f"❌ Produit introuvable")
        messages.error(request, "Produit introuvable")
        return redirect('liste_produits')
    except ValueError as e:
        print(f"❌ Erreur de valeur: {e}")
        messages.error(request, "Quantité invalide")
        return redirect('detail_produit', produit_id=produit_id)
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        messages.error(request, f"Erreur : {str(e)}")
        return redirect('detail_produit', produit_id=produit_id)
@login_required
#@require_http_methods(["POST"])
def modifier_quantite_panier(request, ligne_id):
    """Modifier la quantité d'un article dans le panier"""
    try:
        nouvelle_quantite = int(request.POST.get('quantite', 1))
        ServicePanier.modifier_quantite(request.user.id, ligne_id, nouvelle_quantite)
        messages.success(request, "Quantité mise à jour")
    except (ValidationError, ValueError) as e:
        messages.error(request, str(e))
    
    return redirect('voir_panier')


@login_required
@require_http_methods(["POST"])
def retirer_du_panier(request, ligne_id):
    """Retirer un produit du panier"""
    try:
        ServicePanier.retirer_du_panier(request.user.id, ligne_id)
        messages.success(request, "Article retiré du panier")
    except ValidationError as e:
        messages.error(request, str(e))
    
    return redirect('voir_panier')


@login_required
@require_http_methods(["POST"])
def vider_panier(request):
    """Vider complètement le panier"""
    ServicePanier.vider_panier(request.user.id)
    messages.success(request, "Panier vidé")
    return redirect('voir_panier')


@login_required
def valider_commande(request):
    """Valider la commande"""
    if request.method == 'POST':
        try:
            mode_retrait = request.POST.get('mode_retrait', 'LIVRAISON')
            adresse = request.POST.get('adresse_livraison', '')
            
            commande = ServicePanier.valider_commande(
                request.user.id,
                mode_retrait,
                adresse
            )
            
            messages.success(
                request,
                f"Commande #{commande.id} validée ! Les vendeurs ont été notifiés."
            )
            return redirect('mes_commandes')
            
        except ValidationError as e:
            messages.error(request, str(e))
            return redirect('voir_panier')
    
    # GET : afficher le formulaire de validation
    try:
        details = ServicePanier.obtenir_panier_avec_details(request.user.id)
        
        if details['nombre_articles'] == 0:
            messages.warning(request, "Votre panier est vide")
            return redirect('voir_panier')
        
        context = {
            'panier': details['panier'],
            'vendeurs': details['vendeurs'],
            'montant_total': details['montant_total'],
        }
        
        return render(request, 'agri_market/panier/valider_commande.html', context)
    except Exception as e:
        messages.error(request, f"Erreur: {str(e)}")
        return redirect('voir_panier')


@login_required
def mes_commandes(request):
    """Liste des commandes du client"""
    if request.user.role != 'CLIENT':
        messages.error(request, "Accès réservé aux clients")
        return redirect('liste_produits')
    
    commandes = Commande.objects.filter(
        client=request.user
    ).exclude(
        statut='PANIER'
    ).prefetch_related('lignes__produit__vendeur').order_by('-date_commande')
    
    context = {
        'commandes': commandes
    }
    
    return render(request, 'agri_market/client/mes_commandes.html', context)


# =========================
# GESTION DES COMMANDES VENDEUR
# =========================

@login_required
def commandes_vendeur(request):
    """Liste des commandes reçues par le vendeur"""
    if request.user.role != 'VENDEUR':
        messages.error(request, "Accès réservé aux vendeurs")
        return redirect('liste_produits')
    
    from django.db.models import Sum, F
    
    # Filtrer par statut si demandé
    statut_filtre = request.GET.get('statut', '')
    
    # Récupérer toutes les commandes qui contiennent mes produits
    mes_produits_ids = Produit.objects.filter(vendeur=request.user).values_list('id', flat=True)
    
    commandes_query = Commande.objects.filter(
        lignes__produit_id__in=mes_produits_ids
    ).exclude(statut='PANIER').distinct().select_related('client').prefetch_related('lignes__produit')
    
    if statut_filtre:
        commandes_query = commandes_query.filter(statut=statut_filtre)
    
    commandes_query = commandes_query.order_by('-date_commande')
    
    # Préparer les données avec seulement mes lignes
    commandes_data = []
    for commande in commandes_query:
        mes_lignes = commande.lignes.filter(produit__vendeur=request.user)
        mon_total = sum(ligne.prix_unitaire * ligne.quantite for ligne in mes_lignes)
        
        commandes_data.append({
            'commande': commande,
            'mes_lignes': mes_lignes,
            'mon_total': mon_total
        })
    
    # Statistiques
    stats = {
        'en_attente': Commande.objects.filter(
            lignes__produit__vendeur=request.user,
            statut='EN_ATTENTE'
        ).distinct().count(),
        'payees': Commande.objects.filter(
            lignes__produit__vendeur=request.user,
            statut='PAYEE'
        ).distinct().count(),
        'expediees': Commande.objects.filter(
            lignes__produit__vendeur=request.user,
            statut='EXPEDIEE'
        ).distinct().count(),
        'livrees': Commande.objects.filter(
            lignes__produit__vendeur=request.user,
            statut='LIVREE'
        ).distinct().count(),
    }
    
    context = {
        'commandes': commandes_data,
        'stats': stats,
    }
    
    return render(request, 'agri_market/vendeur/commandes_recues.html', context)


@login_required
#@require_http_methods(["POST"])
def changer_statut_commande(request, commande_id):
    """Changer le statut d'une commande (vendeur)"""
    if request.user.role != 'VENDEUR':
        messages.error(request, "Accès réservé aux vendeurs")
        return redirect('liste_produits')
    
    try:
        commande = Commande.objects.get(id=commande_id)
        nouveau_statut = request.POST.get('statut')
        
        # Vérifier que cette commande contient mes produits
        if not commande.lignes.filter(produit__vendeur=request.user).exists():
            messages.error(request, "Cette commande ne vous concerne pas")
            return redirect('commandes_vendeur')
        
        # Valider la transition de statut
        transitions_valides = {
            'EN_ATTENTE': ['PAYEE', 'ANNULEE'],
            'PAYEE': ['EXPEDIEE', 'ANNULEE'],
            'EXPEDIEE': ['LIVREE'],
        }
        
        if commande.statut in transitions_valides:
            if nouveau_statut in transitions_valides[commande.statut]:
                commande.statut = nouveau_statut
                commande.save()
                messages.success(request, f"Statut mis à jour: {commande.get_statut_display()}")
            else:
                messages.error(request, "Transition de statut invalide")
        else:
            messages.error(request, "Impossible de modifier ce statut")
            
    except Commande.DoesNotExist:
        messages.error(request, "Commande introuvable")
    
    return redirect('commandes_vendeur')


# =========================
# DASHBOARD ADMIN
# =========================

@staff_member_required
def dashboard_admin(request):
    """Dashboard administrateur - accessible uniquement aux superusers"""
    from django.db.models import Count, Q
    
    # Statistiques
    stats = {
        'total_users': Utilisateur.objects.count(),
        'total_vendeurs': Utilisateur.objects.filter(role='VENDEUR').count(),
        'total_clients': Utilisateur.objects.filter(role='CLIENT').count(),
        'total_produits': Produit.objects.count(),
        'total_commandes': Commande.objects.exclude(statut='PANIER').count(),
        'commandes_attente': Commande.objects.filter(statut='EN_ATTENTE').count(),
        'commandes_payees': Commande.objects.filter(statut='PAYEE').count(),
        'commandes_livrees': Commande.objects.filter(statut='LIVREE').count(),
    }
    
    # Listes
    vendeurs = Utilisateur.objects.filter(role='VENDEUR').prefetch_related('produits').order_by('-date_joined')
    clients = Utilisateur.objects.filter(role='CLIENT').prefetch_related('commandes').order_by('-date_joined')
    commandes_recentes = Commande.objects.exclude(statut='PANIER').select_related('client').prefetch_related('lignes').order_by('-date_commande')[:20]
    
    context = {
        'stats': stats,
        'vendeurs': vendeurs,
        'clients': clients,
        'commandes_recentes': commandes_recentes,
    }
    
    return render(request, 'agri_market/admin/dashboard.html', context)


# =========================
# API AJAX (Optionnel)
# =========================

@login_required
def ajuster_stock_ajax(request, produit_id):
    """
    Ajuster le stock via AJAX
    """
    if request.method == 'POST' and request.user.role == 'VENDEUR':
        try:
            quantite_delta = int(request.POST.get('delta', 0))
            
            produit = ServiceProduit.ajuster_stock(
                produit_id=produit_id,
                quantite_delta=quantite_delta
            )
            
            return JsonResponse({
                'success': True,
                'nouvelle_quantite': produit.quantite,
                'message': 'Stock mis à jour'
            })
            
        except (ValidationError, ValueError) as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
    
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'}, status=405)

