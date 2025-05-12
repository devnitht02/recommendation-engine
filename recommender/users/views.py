import json
import re
import smtplib
import uuid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.timezone import now

from institutions.models import WnState, WnDistrict
from recommender import settings
from users.models import WnUser


def is_valid_password(password):
    return bool(re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$', password))


def signup(request):
    if request.method == "POST":
        list(messages.get_messages(request))
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not is_valid_password(password):
            messages.error(request, "Password must be at least 8 characters, with uppercase, lowercase, and a digit.")
            return redirect('users:signup')

        if WnUser.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('users:signin')

        user = WnUser(user_name=name, email=email, password=make_password(password))
        user.save()

        messages.success(request, "Signup successful! Please log in.")
        return redirect('users:signin')
    return render(request, "signup.html")


def signin(request):
    if request.method == 'POST':
        list(messages.get_messages(request))
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = WnUser.objects.filter(email=email).first()

        if not user and not is_valid_password(password):
            messages.error(request, "Both email and password are invalid.")
            return redirect('users:signin')

        if not user:
            messages.error(request, "No account found with that email.")
            return redirect('users:signin')

        if not is_valid_password(password):
            messages.error(request, "Password format is invalid. It must include uppercase, lowercase, and a digit.")
            return redirect('users:signin')

        if not check_password(password, user.password):
            messages.error(request, "Incorrect password.")
            return redirect('users:signin')

        # Valid login
        request.session['user_id'] = user.id
        request.session['user_name'] = user.user_name
        request.session['user_email'] = user.email
        if user.profile_picture:
            request.session['profile_picture'] = user.profile_picture.url
        messages.success(request, "Signed in successfully.")
        user.last_login = now()
        user.save()
        return redirect('dashboard:dashboard')

    return render(request, 'signin.html')


def google_login(request):
    if request.method == 'POST':
        # Get the Google token from the frontend
        data = json.loads(request.body)
        credential = data.get('credential')

        # Verify token with Google
        payload = {
            'id_token': credential,
            'client_id': settings.GOOGLE_CLIENT_ID
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
# @login_required

# @csrf_exempt
def user_profile(request):
    if "user_id" not in request.session:
        return redirect('users:signin')

    wn_user = WnUser.objects.filter(pk=int(request.session['user_id'])).first()
    state = WnState.objects.all()
    district = WnDistrict.objects.all()

    if request.method == 'POST':
        new_user_name = request.POST.get('user_name')
        if new_user_name:  # only update if not empty
            wn_user.user_name = new_user_name
            request.session['user_name'] = new_user_name  # keep header greeting in sync

        wn_user.email = request.POST.get('email')
        wn_user.user_gender = request.POST.get('user_gender')
        wn_user.school_passed_out_year = request.POST.get('school_passed_out_year')
        wn_user.studied_institution_type = request.POST.get('institution_type')
        wn_user.stream = request.POST.get('stream')

        hsc_raw = request.POST.get('hsc_percentage')
        wn_user.hsc_percentage = float(hsc_raw) if hsc_raw else None

        wn_user.state_id = request.POST.get('state')
        wn_user.district_id = request.POST.get('district')

        if request.FILES.get('profile_picture'):
            print("Saving profile picture...")
            wn_user.profile_picture = request.FILES['profile_picture']

        wn_user.save()
        print("User saved:", wn_user.profile_picture)
        if wn_user.profile_picture:
            request.session["profile_picture"] = wn_user.profile_picture.url

        return redirect('users:user_profile')

    context = {
        "profile": wn_user,
        "states": state,
        "districts": district,
    }
    return render(request, 'profile.html', context)


# @csrf_exempt
def upload_profile_picture(request):
    if request.method == 'POST' and request.FILES.get('profile_picture'):
        try:
            user_id = request.session.get('user_id')
            if not user_id:
                return JsonResponse({'status': 'error', 'message': 'Not logged in'}, status=403)

            user = WnUser.objects.get(pk=user_id)
            user.profile_picture = request.FILES['profile_picture']
            user.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


# @csrf_exempt
# @login_required
def update_user_profile(request):
    """Update the user profile based on the incoming data."""
    if request.method == "POST":
        user_id = request.session.get("user_id")

        if user_id:

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


reset_tokens = {}


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = WnUser.objects.filter(email=email).first()

        if not user:
            messages.error(request, "No user with that email.")
            return redirect('users:forgot_password')

        token = uuid.uuid4().hex
        reset_tokens[email] = token

        reset_url = request.build_absolute_uri(
            reverse('users:reset_password') + f"?email={email}&key={token}"
        )

        context = {'reset_url': reset_url, 'user': user}
        html_content = render_to_string("reset_password_email.html", context)

        msg = MIMEMultipart()
        msg['From'] = settings.SMTP_EMAIL
        msg['To'] = email
        msg['Subject'] = "Reset Your Password"
        msg.attach(MIMEText(html_content, 'html'))

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(settings.SMTP_EMAIL, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_EMAIL, email, msg.as_string())
            server.quit()
            messages.success(request, "Check your email for the reset link.")
        except Exception as e:
            messages.error(request, f"Email failed: {e}")

        return redirect('users:signin')

    return render(request, 'reset_password_form.html')


def reset_password(request):
    email = request.GET.get('email')
    key = request.GET.get('key')

    if request.method == 'POST':
        email = request.POST.get('email')
        key = request.POST.get('key')
        password = request.POST.get('password')
        confirm = request.POST.get('confirm_password')

        if key != reset_tokens.get(email):
            return render(request, "new_password.html", {
                "error": "Invalid or expired token"
            })

        if password != confirm:
            return render(request, "new_password.html", {
                "error": "Passwords do not match",
                "email": email,
                "key": key
            })

        user = WnUser.objects.filter(email=email).first()
        if user:
            user.password = make_password(password)
            user.save()
            messages.success(request, "Password reset successfully!")
            return redirect('users:signin')

    return render(request, "new_password.html", {'email': email, 'key': key})
