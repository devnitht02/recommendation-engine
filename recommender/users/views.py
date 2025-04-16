import datetime

from django.contrib.auth import login, get_user_model
from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import now
from django.contrib.auth import login
from recommender import settings
from users.models import WnUser
from institutions.models import WnState, WnDistrict
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
import requests
from django.shortcuts import redirect
from django.http import JsonResponse
from django.conf import settings


def signup(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Check if user already exists
        if WnUser.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('users:signin')

        # Save new user
        user = WnUser(user_name=name, email=email, password=make_password(password))
        user.save()

        # Login user automatically after signup
        request.session['user_id'] = user.id
        request.session['user_name'] = user.user_name
        request.session['user_email'] = user.email

        messages.success(request, "Signup successful! You are now logged in.")
        return redirect('users:signin')

    return render(request, "signup.html")


def signin(request):
    if request.method == 'POST':
        email = request.POST.get("email")
        password = request.POST.get("password")
        # for GOOGLE SIGN IN add the user id username email in the session
        user = WnUser.objects.filter(email=email).first()

        if user and check_password(password, user.password):
            request.session['user_id'] = user.id
            request.session['user_name'] = user.user_name
            request.session['user_email'] = user.email
            # add profile photo here

            messages.success(request, "Signed in successfully.")
            user.last_login = now()
            user.save()
            return redirect('dashboard:dashboard')
        else:
            messages.error(request, "Incorrect email or password.")
            return redirect('users:signin')

    return render(request, 'signin.html')


GOOGLE_CLIENT_ID = "1051342845649-8qlcc0h41kq2sf3dakaogfdgv2omks4p.apps.googleusercontent.com"
GOOGLE_REDIRECT_URI = "http://localhost:8000/google_login/"
GOOGLE_CLIENT_SECRET = "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"


def google_login(request):
    if request.method == 'POST':
        # Get the Google token from the frontend
        data = json.loads(request.body)
        credential = data.get('credential')

        # Verify token with Google
        payload = {
            'id_token': credential,
            'client_id': GOOGLE_CLIENT_ID
        }
        url = 'https://oauth2.googleapis.com/tokeninfo'
        response = requests.get(url, params=payload)

        if response.status_code == 200:
            user_info = response.json()
            email = user_info.get('email')
            name = user_info.get('name')
            google_id = user_info.get('sub')  # Google unique user ID

            # Check if the user already exists in the database
            # User = get_user_model()
            # user, created = User.objects.get_or_create(username=email, defaults={'first_name': name})
            #
            # # If user is new, populate additional fields like last login
            # if created:
            #     user.last_login = datetime.datetime.now()
            #     user.save()
            #
            # # Log the user in
            # login(request, user)
            #

            # Return success response
            return JsonResponse({'status': 'success', 'user': {'username': user.username}})

        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid token'})

    return JsonResponse({'status': 'error', 'message': 'Only POST requests allowed'})


def google_auth_callback(request):
    """Handle Google's OAuth response."""
    code = request.GET.get('code')  # Get the 'code' from the query string
    if not code:
        return JsonResponse({'error': 'No authorization code provided'}, status=400)

    # Exchange authorization code for access token
    token_url = 'https://oauth2.googleapis.com/token'
    token_data = {
        'client_id': settings.GOOGLE_CLIENT_ID,
        'client_secret': settings.GOOGLE_CLIENT_SECRET,
        'code': code,
        'redirect_uri': settings.GOOGLE_REDIRECT_URI,
        'grant_type': 'authorization_code',
    }

    token_response = requests.post(token_url, data=token_data)
    token_json = token_response.json()

    if 'error' in token_json:
        return JsonResponse({'error': token_json['error']}, status=400)

    # Get user info using the access token
    access_token = token_json.get('access_token')
    userinfo_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
    userinfo_response = requests.get(userinfo_url, headers={'Authorization': f'Bearer {access_token}'})
    userinfo = userinfo_response.json()

    if 'email' not in userinfo:
        return JsonResponse({'error': 'Failed to get email from Google'}, status=400)

    # Check if user exists in your database
    email = userinfo['email']
    user_name = userinfo.get('name')
    user, created = WnUser.objects.get_or_create(email=email, defaults={'user_name': user_name})

    # Log the user in
    login(request, user)

    # Redirect to dashboard or profile page
    return redirect('dashboard:dashboard')


def signout(request):
    if 'user_id' in request.session:
        request.session.flush()
        messages.success(request, "You have been logged out.")
    else:
        messages.warning(request, "You are not logged in.")
    return redirect('dashboard:dashboard')


# PROFILE SECTION
# @login_required  # Ensures only logged-in users can access the profile
def user_profile(request):
    """Retrieve the logged-in user's profile details."""
    # user = request.user  # Get the currently logged-in user
    if "user_id" not in request.session:
        return redirect('users:signin')
    print(request.session['user_id'])
    try:
        wn_user = WnUser.objects.filter(pk=int(request.session['user_id'])).first()
        state = WnState.objects.all()
        district = WnDistrict.objects.all()
        print(wn_user)
        context = {
            "profile": wn_user,
            "states": state,
            "districts": district,

        }

        return render(request, 'profile.html', context)
    except WnUser.DoesNotExist:
        return JsonResponse({"status": "error", "message": "User profile not found"}, status=404)


# @csrf_exempt  # Disable CSRF for simplicity, but use CSRF tokens in production
# @login_required
def update_user_profile(request):
    """Update the user profile based on the incoming data."""
    if request.method == "POST":
        user_id = request.session.get("user_id")

        if user_id:
            # Get the data from the POST request
            name = request.POST.get("name")
            email = request.POST.get("email")
            country = request.POST.get("country")
            dob = request.POST.get("dob")
            gender = request.POST.get("gender")
            school_year = request.POST.get("school_year")
            state_id = request.POST.get("state_id")
            district_id = request.POST.get("district_id")
            stream = request.POST.get("stream")
            hsc = request.POST.get("hsc")
            institution_type = request.POST.get("institution_type")

            # Fetch the user and update the fields
            try:
                user = WnUser.objects.get(pk=user_id)
                user.name = name
                user.email = email
                user.country = country
                user.dob = dob
                user.gender = gender
                user.school_year = school_year
                user.state_id = state_id
                user.district_id = district_id
                user.stream = stream
                user.hsc = hsc
                user.institution_type = institution_type
                user.save()

                # Return updated data as response
                return JsonResponse({
                    "name": user.name,
                    "email": user.email,
                    "country": user.country,
                    "dob": user.dob,
                    "gender": user.gender,
                    "school_year": user.school_year,
                    "state_id": user.state_id,
                    "district_id": user.district_id,
                    "stream": user.stream,
                    "hsc": user.hsc,
                    "institution_type": user.institution_type
                })

            except WnUser.DoesNotExist:
                return JsonResponse({"error": "User not found"}, status=404)

    return JsonResponse({"error": "Invalid request"}, status=400)


def get_district(request, state_id):
    try:
        district = list(WnDistrict.objects.filter(state_id=state_id).values())
        return JsonResponse(district, safe=False, status=200)
    except WnUser.DoesNotExist:
        return JsonResponse({"status": "error", "message": "User profile not found"}, status=404)
