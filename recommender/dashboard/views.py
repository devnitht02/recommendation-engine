from django.http import JsonResponse
from django.shortcuts import render

from institutions.models import WnCourse, WnInstitution


# Create your views here.
def dashboard(request):
    course_data = WnCourse.objects.select_related("degree", "stream").all()
    search_suggestion = request.GET.get('query', '')  # Capture the search suggestion if it exists

    return render(request, 'dashboard.html', {'course_data': course_data, 'search_suggestion': search_suggestion})


def search_suggestions(request):
    query = request.GET.get('query', '')
    if query:
        course_results = WnCourse.objects.filter(course_name__icontains=query)
        institution_results = WnInstitution.objects.filter(institution_name__icontains=query)

        data = {
            'courses': [{'course_name': course.course_name} for course in course_results],
            'institutions': [{'institution_name': institution.institution_name} for institution in institution_results]
        }
        return JsonResponse(data)
    else:
        return JsonResponse({'courses': [], 'institutions': []})
