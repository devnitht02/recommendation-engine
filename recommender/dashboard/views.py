import configparser
import os
import smtplib

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect

from institutions.models import WnCourse, WnInstitution
from recommendations.services.recommendation_service import RecommendationService
from recommender.models import WnContact


# Create your views here.
def dashboard(request):
    course_data = WnCourse.objects.select_related("degree", "stream").all()
    institution_data = WnInstitution.objects.select_related("state", "district").all()
    search_suggestion = request.GET.get('query', '')  # Capture the search suggestion if it exists

    return render(request, 'dashboard.html', {'course_data': course_data, 'search_suggestion': search_suggestion,
                                              'institution_data': institution_data})


def search_suggestions(request):
    query = request.GET.get('query', '')
    print(f"Query received: {query}")

    if query:
        ins = RecommendationService()
        search_data = ins.global_search(query)
        # Fetch courses that match the query (case insensitive)
        course_results = WnCourse.objects.filter(course_name__icontains=query)

        # Fetch institutions that match the query (case insensitive)
        institution_results = WnInstitution.objects.filter(institution_name__icontains=query)

        # Prepare data for both courses and institutions with type
        data = {
            'courses': [{'id': course.id, 'course_name': course.course_name, 'type': 'course'} for course in
                        course_results],
            'institutions': [
                {'id': institution.id, 'institution_name': institution.institution_name, 'type': 'institution'} for
                institution in institution_results],
            "search_data": search_data
        }
    else:
        # If query is empty, return empty results for both
        data = {'courses': [], 'institutions': []}

    return JsonResponse(data)



def redirect_to_item(request, item_id):
    # Try to find a course with the given ID
    try:
        course = WnCourse.objects.get(id=item_id)
        return redirect('institutions:view_course', course_id=course.id)
    except WnCourse.DoesNotExist:
        # If no course found, check for an institution
        try:
            institution = WnInstitution.objects.get(id=item_id)
            return redirect('institutions:view_institution', institution_id=institution.id)
        except WnInstitution.DoesNotExist:
            return redirect('dashboard:dashboard')


def get_email_credentials():
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.ini')
    config.read(os.path.abspath(config_path))
    email = config['EMAIL']['SMTP_EMAIL']
    password = config['EMAIL']['SMTP_PASSWORD']
    return email, password


def contact_page(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message_body = request.POST.get("message")

        if WnContact.objects.filter(email=email).exists():
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"status": "error", "reason": "duplicate"})
            messages.error(request, "You've already sent a message with this email.")
            return redirect("dashboard:contact_page")

        contact_info = WnContact(name=name, email=email, subject=subject, message=message_body)
        contact_info.save()

        smtp_email, smtp_password = get_email_credentials()

        try:
            connection = smtplib.SMTP('smtp.gmail.com', 587)
            connection.starttls()
            connection.login(user=smtp_email, password=smtp_password)
            email_message = (
                f"Subject: PathFinder \n\n"
                f"Hey {name}! Thanks for contacting us!. "
                f"Remember, progress comes from perseverance. We'll reach out to you soon—keep up the great work!"
            )
            connection.sendmail(
                from_addr=smtp_email,
                to_addrs=email,
                msg=email_message.encode('utf-8')
            )
            connection.quit()
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
