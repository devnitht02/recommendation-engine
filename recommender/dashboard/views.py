from django.shortcuts import render

from institutions.models import WnCourse


# Create your views here.
def dashboard(request):
    course_data = WnCourse.objects.select_related("degree", "stream").all()

    return render(request, 'dashboard.html', {'course_data': course_data})
