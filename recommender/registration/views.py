from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import render
from registration.models import Registration


def signup(request):
    if request.method == "POST":
        name = request.POST["name"]
        email = request.POST["email"]
        password = request.POST["password"]
        print(name, email, password)

        user_credentials = Registration(username=name, email=email, password=make_password(password))
        user_credentials.save()

        return render(request, "success.html")
    else:
        print("Oops something went wrong!")

    return render(request, 'signup.html')


def signin(request):
    if request.method == 'POST':
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = Registration.objects.filter(email=email).first()

        if user and check_password(password, user.password):
            messages.success(request, "Signed in successfully.")
            return render(request, 'dashboard.html')
        else:
            messages.error(request, "Incorrect email or password.")

    return render(request, 'signin.html')
