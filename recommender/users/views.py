from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import render, redirect
from django.contrib import messages
from users.models import WnUser
from institutions.models import WnState, WnDistrict


def signup(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if WnUser.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('signup')

        user = WnUser(user_name=name, email=email, password=make_password(password))
        user.save()

        messages.success(request, "Signup successful! You can now log in.")
        return render(request, 'success.html')

    return render(request, "signup.html")


def signin(request):
    if request.method == 'POST':
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = WnUser.objects.filter(email=email).first()

        if user and check_password(password, user.password):
            request.session['user_id'] = user.id
            request.session['user_name'] = user.user_name
            request.session['user_email'] = user.email

            messages.success(request, "Signed in successfully.")
            return render(request, 'profile.html')
        else:
            messages.error(request, "Incorrect email or password.")
            return render(request, 'signin.html')

    return render(request, 'signin.html')


def signout(request):
    request.session.flush()
    messages.success(request, "You have been logged out.")
    return render(request, 'dashboard.html')


# PROFILE SECTION

def user(request):
    user_id = request.session.get('user_id')

    if not user_id:
        messages.error(request, "You need to sign in first.")
        return render(request, 'signin.html')

    user = WnUser.objects.filter(id=user_id).first()
    if not user:
        messages.error(request, "User not found. Please sign in again.")
        request.session.flush()
        return render(request, 'signin.html')

    # Fetch user profile
    profile, created = WnUser.objects.get_or_create(
        id=user.id,
        defaults={
            'user_name': user.user_name,
            'email': user.email
        }
    )

    request.session['user_name'] = user.user_name
    request.session['user_email'] = user.email

    if request.method == "POST":
        profile.phone_number = request.POST.get("phone_number", profile.phone_number)
        profile.country = request.POST.get("country", profile.country)
        profile.address = request.POST.get("address", profile.address)
        profile.date_of_birth = request.POST.get("date_of_birth", profile.date_of_birth)
        profile.user_gender = request.POST.get("gender", profile.user_gender)
        profile.stream = request.POST.get("stream", profile.stream)
        profile.hsc_percentage = request.POST.get("percentage", profile.hsc_percentage)
        profile.school_passed_out_year = request.POST.get("year", profile.school_passed_out_year)
        profile.studied_institution_type = request.POST.get("institution", profile.studied_institution_type)

        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES["profile_picture"]

        state_id = request.POST.get("state")
        district_id = request.POST.get("district")

        if state_id:
            profile.state = WnState.objects.filter(id=state_id).first()
        if district_id:
            profile.district = WnDistrict.objects.filter(id=district_id).first()

        profile.save()
        messages.success(request, "Profile updated successfully!")
        return render(request, 'profile.html')

    return render(request, "profile.html", {
        "profile": profile,
        "name": request.session.get('user_name'),
        "email": request.session.get('user_email')
    })
