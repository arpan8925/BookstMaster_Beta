from django.shortcuts import render, redirect



from django.contrib.auth import login, logout, authenticate



from django.contrib.auth.decorators import login_required, permission_required



from django.contrib import messages



from .forms import UserRegistrationForm, UserLoginForm





def User_login_view(request):

    if request.user.is_authenticated:

        return redirect("user_dashboard")



    if request.method == "POST":

        form = UserLoginForm(request, data=request.POST)



        if form.is_valid():

            username = form.cleaned_data.get("username")



            password = form.cleaned_data.get("password")



            user = authenticate(username=username, password=password)



            if user is not None:

                login(request, user)



                return redirect("user_dashboard")



    else:

        form = UserLoginForm()



    return render(request, "authentication/user/login.html", {"form": form})





def register_view(request):

    if request.user.is_authenticated:

        return redirect("user_dashboard")



    if request.method == "POST":

        form = UserRegistrationForm(request.POST, request.FILES)



        if form.is_valid():

            user = form.save()



            login(request, user)



            return redirect("user_dashboard")



    else:

        form = UserRegistrationForm()



    return render(request, "authentication/user/register.html", {"form": form})





@login_required

def logout_view(request):

    logout(request)



    return redirect("home")



def Manager_login_view(request):

    return render(request, "authentication/manager/manager_login.html")



def manager_login(request):

    if request.method == 'POST':

        username = request.POST.get('username')

        password = request.POST.get('password')

        

        user = authenticate(request, username=username, password=password)

        

        if user is not None:

            # Check if user has manager permission

            if user.has_perm('authentication.is_manager'):

                login(request, user)

                return redirect('managerdashboard:manager_dashboard')

            else:

                messages.error(request, 'You do not have manager privileges. Please login as a regular user.')

                return redirect('user_login')

        else:

            messages.error(request, 'Invalid username or password.')

    

    return render(request, 'authentication/manager/manager_login.html')



@permission_required('authentication.is_manager', login_url='manager_login')

def manager_dashboard(request):

    return render(request, 'managerdashboard/dashboard.html')


