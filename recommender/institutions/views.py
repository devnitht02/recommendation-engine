from django.shortcuts import render
from .models import WnInstitution, WnCourse


def institutions(request):
    institution_data = WnInstitution.objects.select_related("state", "district")  # Retrieve all institutions
    return render(request, 'institutions.html', {'institution_data': institution_data})


def courses(request):
    # courses = WnCourse.objects.all()  # Retrieve all institutions

    course_data = WnCourse.objects.select_related("degree", "stream").all()

    return render(request, 'courses.html', {'course_data': course_data})
