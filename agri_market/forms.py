#Formulaire utilisateurs

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Utilisateur


class InscriptionForm(UserCreationForm):
    class Meta:
        model = Utilisateur
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'telephone',
            'role',
            'nom_boutique',      # visible uniquement si role = VENDEUR
            'password1',
            'password2',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendre nom_boutique optionnel par défaut
        self.fields['nom_boutique'].required = False
        self.fields['nom_boutique'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nom de votre boutique / ferme (seulement pour vendeurs)'
        })

        # Classes Bootstrap pour tous les champs
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

        # Champs spécifiques
        self.fields['role'].widget.attrs.update({'class': 'form-select'})
        self.fields['telephone'].widget.attrs.update({'placeholder': '+237 6XX XXX XXX'})


    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        nom_boutique = cleaned_data.get('nom_boutique')

        if role == 'VENDEUR' and not nom_boutique:
            self.add_error('nom_boutique', "Le nom de la boutique est obligatoire pour les vendeurs.")

        return cleaned_data


class ConnexionForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nom d’utilisateur ou email'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Mot de passe'
        })
