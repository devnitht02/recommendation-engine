import configparser
import os
import smtplib
from datetime import timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils import timezone

from institutions.models import WnCourse, WnStream, WnState, WnSelectedCourse
from institutions.models import WnInstitution
from recommendations.services.course_hybrid import CourseHybrid
from recommendations.services.institution_hybrid import InstitutionHybrid
from recommendations.services.recommendation_service import RecommendationService
from recommender import settings
from recommender.models import WnContact
from users.models import WnUser


def user_selection_model(user_id):
    registration_data = WnUser.objects.filter(pk=user_id).first()
    if not registration_data:
        return False

    input_plus_10 = registration_data.created_date + timedelta(days=10)
    today = timezone.now()
    if input_plus_10 > today:
        return False

    if (WnSelectedCourse.objects.filter(user_id=user_id).exists()):
        return False

    return True


def dashboard(request):
    if "user_id" not in request.session:
        return redirect("users:signin")
    course_data = WnCourse.objects.select_related("degree", "stream").all()
    institution_data = WnInstitution.objects.select_related("state", "district").all()
    search_suggestion = request.GET.get('query', '')
    top_ranked_courses = WnCourse.objects.filter(rank__isnull=False).order_by('rank')[:27]
    top_ranked_institutions = WnInstitution.objects.filter(rank__isnull=False).order_by('rank')[:20]
    user_id = request.session["user_id"]
    streams = WnStream.objects.filter(active='1')

    institution_hybrid = InstitutionHybrid().get_hybrid_institutions(user_id)
    course_hybrid = CourseHybrid().get_hybrid_courses(user_id)
    context = {
        'course_data': course_data,
        'search_suggestion': search_suggestion,
        'institution_data': institution_data,
        'top_ranked_courses': top_ranked_courses,
        'top_ranked_institutions': top_ranked_institutions,
        "institution_hybrid": institution_hybrid,
        "course_hybrid": course_hybrid,
        "streams": streams,
        'MEDIA_URL': settings.MEDIA_URL,
        'states': WnState.objects.filter(active=1),
        'institution_selection_model': user_selection_model(user_id),
    }

    return render(request, 'dashboard.html', context)


def search_suggestions(request):
    query = request.GET.get('query', '')
    print(f"Query received: {query}")

    if query:
        ins = RecommendationService()
        search_data = ins.global_search(query)

        # search_data = search_engine.search(query)

        course_results = WnCourse.objects.filter(course_name__icontains=query)

        institution_results = WnInstitution.objects.filter(institution_name__icontains=query)

        data = {
            'courses': [{'id': course.id, 'course_name': course.course_name, 'type': 'course'} for course in
                        course_results],
            'institutions': [
                {'id': institution.id, 'institution_name': institution.institution_name, 'type': 'institution'} for
                institution in institution_results],
            "search_data": search_data
        }
    else:

        data = {'courses': [], 'institutions': []}

    return JsonResponse(data)


def redirect_to_item(request, item_id):
    try:
        course = WnCourse.objects.get(id=item_id)
        return redirect('institutions:view_course', course_id=course.id)
    except WnCourse.DoesNotExist:

        try:
            institution = WnInstitution.objects.get(id=item_id)
            return redirect('institutions:view_institution', institution_id=institution.id)
        except WnInstitution.DoesNotExist:
            return redirect('dashboard:dashboard')


def get_email_credentials():
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(__file__), '..', 'static/../config.ini')
    config.read(os.path.abspath(config_path))
    email = config['EMAIL']['SMTP_EMAIL']
    password = config['EMAIL']['SMTP_PASSWORD']
    return email, password


def contact_page(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message_body = request.POST.get("message")

        if WnContact.objects.filter(email=email).exists():
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"status": "error", "reason": "duplicate"})
            messages.error(request, "You've already sent a message with this email.")
            return redirect("dashboard:contact_page")

        WnContact.objects.create(name=name, email=email, message=message_body)

        smtp_email, smtp_password = get_email_credentials()
        context = {"name": name, "message": message_body}
        html_message = render_to_string("contact_email_form.html", context)

        try:
            msg = MIMEMultipart()
            msg['From'] = smtp_email
            msg['To'] = email
            msg['Subject'] = "Thank you for contacting PathFinder"
            msg.attach(MIMEText(html_message, 'html'))

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(smtp_email, smtp_password)
            server.sendmail(smtp_email, email, msg.as_string())
            server.quit()
        except Exception as e:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"status": "error", "reason": "email_fail", "details": str(e)})
            messages.error(request, f"Failed to send email: {str(e)}")
            return redirect("dashboard:contact_page")

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({"status": "success"})

        messages.success(request, "Message sent successfully!")
        return redirect("dashboard:dashboard")

    return render(request, "contact.html", {"current_user": request.user})


def about(request):
    return render(request, 'about.html')
