from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import now

from institutions.models import WnDegree, WnInstitutionChoice, WnCourseChoice,WnSelectedCourse
from recommender.models import WnFavourite
from users.models import WnUser
from .models import WnInstitution, WnCourse
from recommendations.services.institution_hybrid import InstitutionHybrid
from recommendations.services.course_hybrid import CourseHybrid
from recommendations.services.institution_hybrid import InstitutionHybrid
from recommender.models import WnFavourite
from users.models import WnUser, WnDistrict, WnState
from .models import WnInstitution, WnCourse


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
                'favourite_institution' : favourite_institution,
                'recommend_institution': InstitutionHybrid().get_hybrid_institutions(user_id,9),
                'liked_institution' : WnInstitutionChoice.objects.filter(user_id=user_id,active="1").values_list("institution_id",flat=True)
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
        'recommend_course' : CourseHybrid().get_hybrid_courses(user_id,9),
        'liked_course' : WnCourseChoice.objects.filter(user_id=user_id,active="1").values_list("course_id",flat=True)
    })


def view_course(request, course_id):
    if "user_id" not in request.session:
        return redirect("users:signin")
    
    course = get_object_or_404(WnCourse, pk=course_id)
    user_id = request.session["user_id"]
    favourite_data = WnFavourite.objects.filter(user_id=user_id)
    favourite_course = [data.course.pk for data in favourite_data if hasattr(data, "course") and data.course]
    
    return render(request, 'view_course.html', {
            'course': course,
            'liked_course' : WnCourseChoice.objects.filter(user_id=user_id,active="1").values_list("course_id",flat=True),
            'favourite_course' : favourite_course,
        })


def view_institution(request, institution_id):
    if "user_id" not in request.session:
        return redirect("users:signin")
    institution_data = get_object_or_404(WnInstitution, pk=institution_id)
    user_id = request.session["user_id"]
    # all courses related to the institution using the WnInstitutionCourse table
    course_data = WnCourse.objects.filter(wninstitutioncourse__institution=institution_data)
    course_data = course_data.select_related('degree', 'stream')

    degree_data = WnDegree.objects.all()
    favourite_data = WnFavourite.objects.filter(user_id=user_id)
    favourite_institution = [data.institution.pk for data in favourite_data if
                             hasattr(data, "institution") and data.institution]

    return render(request, 'view_institution.html', {
        'course_data': course_data,
        'degree_data': degree_data,
        'institution_data': institution_data,
        'favourite_institution' : favourite_institution,
        'liked_institution' : WnInstitutionChoice.objects.filter(user_id=user_id,active="1").values_list("institution_id",flat=True)
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
                favourite_course = WnFavourite.objects.filter(user=wn_user,course_id = course_id)
                if favourite_course.exists():
                    favourite_course.delete()
                    return JsonResponse({'status': 'removed', 'type': 'course'})
                
                ins = WnFavourite(user=wn_user, course_id=course_id)
                ins.save()
                return JsonResponse({'status': 'added', 'type': 'course'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

        if institution_id:
            try:
                favourite_institution = WnFavourite.objects.filter(user=wn_user,institution_id = institution_id)
                if favourite_institution.exists():
                    favourite_institution.delete()
                    return JsonResponse({'status': 'removed', 'type': 'institution'})
                
                ins = WnFavourite(user=wn_user, institution_id=institution_id)
                ins.save()
                return JsonResponse({'status': 'added', 'type': 'institution'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

        return JsonResponse({'status': 'error', 'message': 'Missing IDs'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def like_institution(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        institution_id = request.POST.get('institution_id')

        # Get the Django user from session
        if not 'user_id' in request.session:
            return JsonResponse({'status': 'error', 'message': 'Login required'}, status=403)

        user_id = request.session['user_id']

        try:
            choice_data = WnInstitutionChoice.objects.filter(user=user_id, institution_id=institution_id)
            if not choice_data.exists():
                ins = WnInstitutionChoice(user_id = user_id, institution_id = institution_id)
                ins.save()
            else:
                flag = '0' if choice_data[0].active == '1' else '1'
                choice_data.update(active=flag)
            return JsonResponse({'status': 'added', 'type': 'course'})
        except:
            return JsonResponse({'status': 'error', 'message': 'server error'}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
    
def like_course(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        course_id = request.POST.get('course_id')

        # Get the Django user from session
        if not 'user_id' in request.session:
            return JsonResponse({'status': 'error', 'message': 'Login required'}, status=403)

        user_id = request.session['user_id']

        try:
            choice_data = WnCourseChoice.objects.filter(user=user_id, course_id=course_id)
            if not choice_data.exists():
                ins = WnCourseChoice(user_id = user_id, course_id = course_id)
                ins.save()
            else:
                flag = '0' if choice_data[0].active == '1' else '1'
                choice_data.update(active=flag)
            return JsonResponse({'status': 'added', 'type': 'course'})
        except:
            return JsonResponse({'status': 'error', 'message': 'server error'}, status=500)
    else:
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

    if request.method == 'POST':
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({"message":"Please log in to continue."},status=403)
        
        institution_id = request.POST.get('institution')
        course_id = request.POST.get('course')

        invalid_fields = []
        if not institution_id:
            invalid_fields.append('institution')

        if not course_id:
            invalid_fields.append('course')

        if invalid_fields:
            return JsonResponse({"message": f"{', '.join(invalid_fields)} fields are required" },status=400)
        

        if(WnSelectedCourse.objects.filter(user_id=user_id).exists()):
            return JsonResponse({"message":"A selection has already been made. You can only choose one institution and program"},status=409)
        
        WnSelectedCourse.objects.create(
            user_id=user_id,
            course_id=course_id,
            institution_id=institution_id,
        )
        return JsonResponse({"message" : "success"})

    # return render(request, 'select_course_form.html', {'states': states})


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
