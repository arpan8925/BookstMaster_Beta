from django.shortcuts import render



def home(request):

    return render(request, 'frontend/coming_soon.html')



def about(request):

    return render(request, 'frontend/about.html')



def contact(request):

    return render(request, 'frontend/contact.html')


