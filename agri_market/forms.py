# #Formulaire utilisateurs

# from django import forms
# from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
# from .models import Utilisateur


# from django import forms
# from .models import Utilisateur

# class InscriptionForm(forms.ModelForm):
#     mot_de_passe = forms.CharField(widget=forms.PasswordInput)
#     mot_de_passe_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirmez le mot de passe")
    
#     class Meta:
#         model = Utilisateur
#         fields = ['nom', 'prenom', 'email', 'role', 'nom_boutique', 'mot_de_passe', 'mot_de_passe_confirm']
    
#     def clean(self):
#         cleaned_data = super().clean()
#         mp1 = cleaned_data.get("mot_de_passe")
#         mp2 = cleaned_data.get("mot_de_passe_confirm")
#         if mp1 != mp2:
#             raise forms.ValidationError("Les mots de passe ne correspondent pas")
#         return cleaned_data
    
#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.set_password(self.cleaned_data["mot_de_passe"])
#         if commit:
#             user.save()
#         return user



# class ConnexionForm(AuthenticationForm):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['username'].widget.attrs.update({
#             'class': 'form-control',
#             'placeholder': 'Nom d’utilisateur ou email'
#         })
#         self.fields['password'].widget.attrs.update({
#             'class': 'form-control',
#             'placeholder': 'Mot de passe'
#         })
