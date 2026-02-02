"""
Context processors pour rendre des données disponibles dans tous les templates
"""

from .models import Commande


def panier_count(request):
    """
    Ajouter le nombre d'articles dans le panier à tous les templates
    """
    count = 0
    
    if request.user.is_authenticated and hasattr(request.user, 'role'):
        if request.user.role == 'CLIENT':
            try:
                panier = Commande.objects.filter(
                    client=request.user,
                    statut='PANIER'
                ).prefetch_related('lignes').first()
                
                if panier:
                    count = panier.lignes.count()
            except:
                pass
    
    return {
        'panier_count': count
    }
