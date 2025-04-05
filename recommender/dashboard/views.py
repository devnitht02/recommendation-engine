from django.http import JsonResponse
from django.shortcuts import render, redirect

from institutions.models import WnCourse, WnInstitution
from recommendations.services.recommendation_service import RecommendationService


# Create your views here.
def dashboard(request):
    course_data = WnCourse.objects.select_related("degree", "stream").all()
    search_suggestion = request.GET.get('query', '')  # Capture the search suggestion if it exists

    return render(request, 'dashboard.html', {'course_data': course_data, 'search_suggestion': search_suggestion})


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


# Redirect function (new)
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
            return redirect('dashboard:dashboard')  # Fallback to dashboard if no course/institution found


def contact_page(request):
    if request.method == "POST":
        email = request.POST.get("name")
        subject = request.POST.get("subject")



    return render(request, 'contact.html')
