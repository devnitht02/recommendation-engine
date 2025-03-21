from django.shortcuts import render, get_object_or_404

from recommender.models import WnDegree
from .models import WnInstitution, WnCourse


def institutions(request):
    institution_data = WnInstitution.objects.select_related("state", "district")
    return render(request, 'institutions.html', {'institution_data': institution_data})


def courses(request):
    course_data = WnCourse.objects.select_related("degree", "stream").all()
    degree_data = WnDegree.objects.all()
    return render(request, 'courses.html', {'course_data': course_data, 'degree_data': degree_data})


def view_course(request, course_id):
    course = get_object_or_404(WnCourse, pk=course_id)  # Fetch course by ID
    return render(request, 'view_course.html', {'course': course})

def view_institution(request):
    course_data = WnCourse.objects.select_related("degree", "stream").all()
    degree_data = WnDegree.objects.all()
    return render(request, 'view_institution.html', {'course_data': course_data, 'degree_data': degree_data})
