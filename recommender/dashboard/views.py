import configparser
import os
import smtplib

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render
from institutions.models import WnCourse
from institutions.models import WnInstitution
from recommendations.services.recommendation_service import RecommendationService
from recommendations.services.institution_hybrid import InstitutionHybrid
from recommendations.services.course_hybrid import CourseHybrid
from recommender.models import WnContact


def dashboard(request):
    course_images = {
        "computer application": "https://images.pexels.com/photos/3862140/pexels-photo-3862140.jpeg",
        "economics, computer science, statistics": "https://images.pexels.com/photos/590022/pexels-photo-590022.jpeg",
        "economics, computer application and political science": "https://images.pexels.com/photos/669619/pexels-photo-669619.jpeg",
        "business administration": "https://images.pexels.com/photos/3184465/pexels-photo-3184465.jpeg",
        "accounting and financial management": "https://images.pexels.com/photos/3944403/pexels-photo-3944403.jpeg",
        "economics, journalism and mass communication": "https://images.pexels.com/photos/261679/pexels-photo-261679.jpeg",
        "economics, journalism, kannada": "https://images.pexels.com/photos/267569/pexels-photo-267569.jpeg",
        "development economics": "https://images.pexels.com/photos/353667/pexels-photo-353667.jpeg",
        "economics, computer application, applied statistics": "https://images.pexels.com/photos/590022/pexels-photo-590022.jpeg",
        "economics, computer applications, psychology": "https://images.pexels.com/photos/356043/pexels-photo-356043.jpeg",
        "design(honours)": "https://images.pexels.com/photos/296895/pexels-photo-296895.jpeg",
        "economics and history": "https://images.pexels.com/photos/207216/pexels-photo-207216.jpeg",
        "english literature": "https://images.pexels.com/photos/818996/pexels-photo-818996.jpeg",
        "journalism": "https://images.pexels.com/photos/374820/pexels-photo-374820.jpeg",
        "advertising and sales management": "https://images.pexels.com/photos/3183168/pexels-photo-3183168.jpeg",
        "criminology and police administration": "https://images.pexels.com/photos/4506105/pexels-photo-4506105.jpeg",
        "economics": "https://images.pexels.com/photos/4386373/pexels-photo-4386373.jpeg",
        "english, hindi, political science": "https://images.pexels.com/photos/540518/pexels-photo-540518.jpeg",
        "economics with foreign trade": "https://images.pexels.com/photos/257362/pexels-photo-257362.jpeg",
    }

    # institution_images = {
    #     "iit": "https://images.pexels.com/photos/3844581/pexels-photo-3844581.jpeg",
    #     "nit": "https://images.pexels.com/photos/256559/pexels-photo-256559.jpeg",
    #     "university": "https://images.pexels.com/photos/207691/pexels-photo-207691.jpeg",
    #     "institute of technology": "https://images.pexels.com/photos/256541/pexels-photo-256541.jpeg",
    #     "college": "https://images.pexels.com/photos/1184578/pexels-photo-1184578.jpeg",
    #     "engineering": "https://images.pexels.com/photos/256559/pexels-photo-256559.jpeg",
    #     "management": "https://images.pexels.com/photos/3184298/pexels-photo-3184298.jpeg",
    #     "medical": "https://images.pexels.com/photos/3844581/pexels-photo-3844581.jpeg",
    #     "law": "https://images.pexels.com/photos/6077322/pexels-photo-6077322.jpeg",
    # }

    course_data = WnCourse.objects.select_related("degree", "stream").all()
    institution_data = WnInstitution.objects.select_related("state", "district").all()
    search_suggestion = request.GET.get('query', '')
    top_ranked_courses = WnCourse.objects.filter(rank__isnull=False).order_by('rank')[:20]
    top_ranked_institutions = WnInstitution.objects.filter(rank__isnull=False).order_by('rank')[:20]
    user_id = request.session["user_id"]

    for course in top_ranked_courses:
        assigned = False
        name = course.course_name.lower()
        for key, url in course_images.items():
            if key in name:
                course.image_url = url
                assigned = True
                break
        if not assigned:
            course.image_url = "https://via.placeholder.com/400x200?text=No+Image"

    # for institution in top_ranked_institutions:
    #     assigned = False
    #     name = institution.institution_name.lower()
    #     for key, url in institution_images.items():
    #         if key in name:
    #             institution.image_url = url
    #             assigned = True
    #             break
    #     if not assigned:
    #         institution.image_url = "https://via.placeholder.com/400x200?text=No+Image"

    institution_hybrid = InstitutionHybrid().get_hybrid_institutions(1)
    course_hybrid = CourseHybrid().get_hybrid_courses(1)
    context = {
        'course_data': course_data, 
        'search_suggestion': search_suggestion,
        'institution_data': institution_data,
        'top_ranked_courses': top_ranked_courses,
        'top_ranked_institutions': top_ranked_institutions,
        "institution_hybrid" : institution_hybrid,
        "course_hybrid" : course_hybrid
    }

    return render(request, 'dashboard.html', context)


def search_suggestions(request):
    query = request.GET.get('query', '')
    print(f"Query received: {query}")

    if query:
        ins = RecommendationService()
        search_data = ins.global_search(query)

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
