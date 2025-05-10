from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils.timezone import now

from institutions.models import WnDegree, WnSelectedCourse
from recommendations.services.course_hybrid import CourseHybrid
from recommendations.services.institution_hybrid import InstitutionHybrid
from recommender import settings
from users.models import WnDistrict, WnState
from .models import WnInstitution


def institutions(request):
    institution_data = WnInstitution.objects.select_related("state", "district")
    wn_user = None
    if request.user.is_authenticated:
        wn_user = WnUser.objects.filter(email=request.user.email).first()

    user_id = request.session["user_id"]

    favourite_data = WnFavourite.objects.filter(user_id=user_id)
    favourite_institution = [data.institution.pk for data in favourite_data if
                             hasattr(data, "institution") and data.institution]

    search_suggestion_institutions = request.GET.get('query', '')
    context = {
        'institution_data': institution_data,
        'search_suggestions_institutions': search_suggestion_institutions,
        'wn_user': wn_user,
        'favourite_institution': favourite_institution,
        'recommend_institution': InstitutionHybrid().get_hybrid_institutions(user_id, 9)
    }
    return render(request, 'institutions.html', context)


def courses(request):
    user_id = request.session["user_id"]
    course_data = WnCourse.objects.select_related("degree", "stream").all()
    degree_data = WnDegree.objects.all()

    wn_user = None
    if request.user.is_authenticated:
        wn_user = WnUser.objects.filter(email=request.user.email).first()

    favourite_data = WnFavourite.objects.filter(user_id=user_id)
    favourite_course = [data.course.pk for data in favourite_data if hasattr(data, "course") and data.course]

    return render(request, 'courses.html', {
        'course_data': course_data,
        'degree_data': degree_data,
        'wn_user': wn_user,
        'favourite_course': favourite_course,
        'MEDIA_URL': settings.MEDIA_URL,
        'recommend_course': CourseHybrid().get_hybrid_courses(user_id, 9)
    })


from django.shortcuts import render, get_object_or_404
from recommender.models import WnFavourite
from users.models import WnUser
from .models import WnCourse


def view_course(request, course_id):
    course = get_object_or_404(WnCourse, pk=course_id)

    wn_user = None
    favourite_course = []

    if request.user.is_authenticated and 'user_id' in request.session:
        user_id = request.session['user_id']
        wn_user = WnUser.objects.filter(pk=user_id).first()

        # Get all favourited course IDs for this user
        favourite_course = list(
            WnFavourite.objects.filter(user=wn_user)
            .exclude(course=None)
            .values_list('course_id', flat=True)
        )

    return render(request, 'view_course.html', {
        'course': course,
        'favourite_course': favourite_course,  # Used for template condition
        'wn_user': wn_user
    })


def view_institution(request, institution_id):
    institution_data = get_object_or_404(WnInstitution, pk=institution_id)

    # Fetch courses offered
    course_data = WnCourse.objects.filter(wninstitutioncourse__institution=institution_data).select_related('degree',
                                                                                                            'stream')

    degree_data = WnDegree.objects.all()

    wn_user = None
    favourite_institution = []

    if request.user.is_authenticated and 'user_id' in request.session:
        user_id = request.session['user_id']
        wn_user = WnUser.objects.filter(pk=user_id).first()

        # Get all favourited institution IDs for this user
        favourite_institution = list(
            WnFavourite.objects.filter(user=wn_user)
            .exclude(institution=None)
            .values_list('institution_id', flat=True)
        )

    return render(request, 'view_institution.html', {
        'institution_data': institution_data,
        'course_data': course_data,
        'degree_data': degree_data,
        'favourite_institution': favourite_institution,
        'wn_user': wn_user
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


def favourites(request):
    if 'user_id' not in request.session:
        return render(request, 'favourites.html', {'favourite': None, 'anonymous': True})

    wn_user = WnUser.objects.filter(pk=request.session['user_id']).first()
    if wn_user:
        favourite = WnFavourite.objects.filter(user=wn_user)
        return render(request, 'favourites.html', {'favourite': favourite, 'anonymous': False})

    return render(request, 'favourites.html', {'favourite': None, 'anonymous': True})


def toggle_favourite(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        course_id = request.POST.get('course_id')
        institution_id = request.POST.get('institution_id')

        # Get the Django user from session
        if not 'user_id' in request.session:
            return JsonResponse({'status': 'error', 'message': 'Login required'}, status=403)

        try:
            wn_user = WnUser.objects.get(pk=request.session['user_id'])
        except WnUser.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'WnUser not linked'}, status=404)

        if course_id:
            try:
                course = WnCourse.objects.get(id=course_id)
                print(wn_user)
                print(course)
                # created = WnFavourite.objects.create(user=wn_user, course=course)
                ins = WnFavourite(user=wn_user, course=course)
                ins.save()
                if not ins:
                    # fav.delete()
                    return JsonResponse({'status': 'removed', 'type': 'course'})
                return JsonResponse({'status': 'added', 'type': 'course'})
            except WnCourse.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Course not found'}, status=404)

        if institution_id:
            try:
                institution = WnInstitution.objects.get(id=institution_id)
                fav, created = WnFavourite.objects.get_or_create(user=wn_user, institution=institution)
                if not created:
                    fav.delete()
                    return JsonResponse({'status': 'removed', 'type': 'institution'})
                return JsonResponse({'status': 'added', 'type': 'institution'})
            except WnInstitution.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Institution not found'}, status=404)

        return JsonResponse({'status': 'error', 'message': 'Missing IDs'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


# @csrf_exempt
def remove_favourite(request):
    if request.method == "POST":

        user_id = request.session.get("user_id")
        if not user_id:
            return redirect('institutions:favourites')

        wn_user = WnUser.objects.filter(pk=user_id).first()
        if not wn_user:
            return redirect('institutions:favourites')

        course_id = request.POST.get("course_id")
        institution_id = request.POST.get("institution_id")

        if course_id:
            WnFavourite.objects.filter(user=wn_user, course_id=course_id).delete()
        elif institution_id:
            WnFavourite.objects.filter(user=wn_user, institution_id=institution_id).delete()

    return redirect('institutions:favourites')


def course_selection_form(request):
    states = WnState.objects.all()

    if request.method == 'POST':
        user_id = request.session.get('user_id')
        state_id = request.POST.get('state')
        district_id = request.POST.get('district')
        institution_id = request.POST.get('institution')
        course_id = request.POST.get('course')

        if user_id and institution_id and course_id:
            WnSelectedCourse.objects.create(
                user_id=user_id,
                course_id=course_id,
                institution_id=institution_id,
                created_date=now(),
                modified_date=now(),
                active='Y'
            )
            return redirect('dashboard:dashboard')

    return render(request, 'select_course_form.html', {'states': states})


def get_districts(request, state_id):
    districts = WnDistrict.objects.filter(state_id=state_id).values('id', 'name')
    return JsonResponse(list(districts), safe=False)


def get_institutions(request, state_id, district_id):
    institutions = WnInstitution.objects.filter(state_id=state_id, district_id=district_id).values('id',
                                                                                                   'institution_name')
    return JsonResponse(list(institutions), safe=False)


def get_courses(request, institution_id):
    courses = WnCourse.objects.filter(wninstitutioncourse__institution_id=institution_id).values('id', 'course_name')
    return JsonResponse(list(courses), safe=False)
