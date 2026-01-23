
from django.shortcuts import render


def index(request):
    print('Blog')
    return render(request,"index.html")

def contact(request):
    return render(request,"contact.html")

def profile(request):
    return render(request,"profile.html")