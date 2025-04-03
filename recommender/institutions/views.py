from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from recommender.models import WnDegree
from .models import WnInstitution, WnCourse


def institutions(request):
    institution_data = WnInstitution.objects.select_related("state", "district")
    search_suggestion_institutions = request.GET.get('query', '')
    return render(request, 'institutions.html', {'institution_data': institution_data,
                                                 'search_suggestions_institutions': search_suggestion_institutions})


def courses(request):
    course_data = WnCourse.objects.select_related("degree", "stream").all()
    degree_data = WnDegree.objects.all()
    return render(request, 'courses.html', {'course_data': course_data, 'degree_data': degree_data})


def favourites(request):
    return render(request, 'favourites.html')


def view_course(request, course_id):
    course = get_object_or_404(WnCourse, pk=course_id)
    return render(request, 'view_course.html', {'course': course})


def view_institution(request, institution_id):
    institution_data = get_object_or_404(WnInstitution, pk=institution_id)

    # all courses related to the institution using the WnInstitutionCourse table
    course_data = WnCourse.objects.filter(wninstitutioncourse__institution=institution_data)
    course_data = course_data.select_related('degree', 'stream')

    degree_data = WnDegree.objects.all()

    return render(request, 'view_institution.html', {
        'course_data': course_data,
        'degree_data': degree_data,
        'institution_data': institution_data
    })


def search_suggestions_courses(request):
    query = request.GET.get('query', '').strip()
    if query:
        # Fetch courses based on the query
        courses = WnCourse.objects.filter(course_name__icontains=query)
        course_data = [{'course_id': course.id, 'course_name': course.course_name} for course in courses]
        return JsonResponse({'courses': course_data})
    else:
        return JsonResponse({'courses': []})


def search_suggestions_institutions(request):
    query = request.GET.get('query', '').strip()
    if query:
        institutions = WnInstitution.objects.filter(institution_name__icontains=query)
        # Serialize QuerySet to list of dictionaries
        institution_data = [{'institution_id': institution.id, 'institution_name': institution.institution_name} for
                            institution in institutions]
        return JsonResponse({'institutions': institution_data})
    else:
        return JsonResponse({'institutions': []})
