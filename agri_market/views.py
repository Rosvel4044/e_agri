from django.shortcuts import render

# Create your views here.


from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from agri_market.forms import InscriptionForm, ConnexionForm


def inscription(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Connexion automatique après inscription
            login(request, user)
            messages.success(request, "Compte créé avec succès ! Bienvenue.")
            #return redirect('accueil')
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = InscriptionForm()

    return render(request, 'inscription.html', {'form': form})


def connexion(request):
    if request.method == 'POST':
        form = ConnexionForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Bienvenue {user.get_full_name() or user.username} !")
            #return redirect('accueil')
        else:
            messages.error(request, "Identifiants incorrects.")
    else:
        form = ConnexionForm()

    return render(request, 'connexion.html', {'form': form})


#def accueil(request):
    # Page d'accueil après connexion
    # Tu pourras afficher un message de bienvenue différent selon le rôle
    #context = {
    #    'user_role': request.user.role if request.user.is_authenticated else None
    #}
    #return render(request, 'accueil.html', context)



from django.shortcuts import render

def accueil(request):
    return render(request, 'accueil.html', {})  # template simple à créer
