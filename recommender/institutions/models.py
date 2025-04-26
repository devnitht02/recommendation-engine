from django.db import models
from users.models import WnDistrict, WnState, WnUser
# from courses.models import WnCourse


class WnInstitution(models.Model):
    institution_name = models.CharField(max_length=500, blank=True, null=True)
    website = models.TextField(blank=True, null=True)
    institution_type = models.ForeignKey('WnInstitutionType', models.DO_NOTHING, db_column='institution_type',
                                         blank=True, null=True)
    state = models.ForeignKey(WnState, models.DO_NOTHING)
    district = models.ForeignKey(WnDistrict, models.DO_NOTHING)
    rank = models.PositiveIntegerField(blank=True, null=True, db_column='rank')
    created_date = models.DateTimeField()
    modified_date = models.DateTimeField()
    active = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'wn_institution'


class WnInstitutionType(models.Model):
    type = models.CharField(max_length=500, blank=True, null=True)
    created_date = models.DateTimeField()
    modified_date = models.DateTimeField()
    active = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'wn_institution_type'


class WnInstitutionChoice(models.Model):
    user = models.ForeignKey(WnUser, models.DO_NOTHING)
    institution = models.ForeignKey(WnInstitution, models.DO_NOTHING)
    created_date = models.DateTimeField()
    modified_date = models.DateTimeField()
    active = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'wn_institution_choice'
        unique_together = (('user', 'institution'),)


class WnInstitutionCourse(models.Model):
    institution = models.OneToOneField(WnInstitution, models.DO_NOTHING,
                                       primary_key=True)
    course = models.ForeignKey("WnCourse", models.DO_NOTHING)
    created_date = models.DateTimeField()
    modified_date = models.DateTimeField()
    active = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'wn_institution_course'
        unique_together = (('institution', 'course'),)


class WnLocationChoice(models.Model):
    user = models.ForeignKey(WnUser, models.DO_NOTHING, db_column='user')
    state = models.ForeignKey(WnState, models.DO_NOTHING, db_column='state')
    district = models.ForeignKey(WnDistrict, models.DO_NOTHING, db_column='district')
    created_date = models.DateTimeField()
    modified_date = models.DateTimeField()
    active = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'wn_location_choice'
        unique_together = (('user', 'state', 'district'),)


# courses

class WnCourse(models.Model):
    course_name = models.CharField(max_length=255)
    course_description = models.TextField()
    stream = models.ForeignKey('WnStream', models.DO_NOTHING, db_column='stream')
    degree = models.ForeignKey('WnDegree', models.DO_NOTHING, db_column='degree')
    rank = models.IntegerField(null=True, blank=True, db_column='rank')
    degree_price = models.IntegerField(blank=True, null=True, db_column='degree_price')
    duration_years = models.IntegerField(blank=True, null=True, db_column='duration_years')
    image_url = models.ImageField(upload_to='top_rated_courses/', null=True, blank=True)
    created_date = models.DateTimeField()
    modified_date = models.DateTimeField()
    active = models.CharField(max_length=1)


    class Meta:
        managed = False
        db_table = 'wn_course'


class WnCourseChoice(models.Model):
    user = models.ForeignKey(WnUser, models.DO_NOTHING, db_column='user')
    course = models.ForeignKey(WnCourse, models.DO_NOTHING, db_column='course')
    created_date = models.DateTimeField()
    modified_date = models.DateTimeField()
    active = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'wn_course_choice'
        unique_together = (('user', 'course'),)


class WnDegree(models.Model):
    degree_name = models.CharField(max_length=50, blank=True, null=True)
    degree_description = models.CharField(max_length=255, blank=True, null=True)
    created_date = models.DateTimeField()
    modified_date = models.DateTimeField()
    active = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'wn_degree'


class WnStream(models.Model):
    stream_name = models.CharField(max_length=500, blank=True, null=True)
    created_date = models.DateTimeField()
    modified_date = models.DateTimeField()
    image_url = models.ImageField(upload_to='course_images/', null=True, blank=True)
    active = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'wn_stream'


class WnStreamChoice(models.Model):
    user = models.ForeignKey(WnUser, models.DO_NOTHING, db_column='user')
    stream = models.ForeignKey(WnStream, models.DO_NOTHING, db_column='stream')
    created_date = models.DateTimeField()
    modified_date = models.DateTimeField()
    active = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'wn_stream_choice'
        unique_together = (('user', 'stream'),)


class WnSelectedCourse(models.Model):
    user = models.ForeignKey(WnUser, models.DO_NOTHING)
    course = models.ForeignKey(WnCourse, models.DO_NOTHING)
    institution = models.ForeignKey(WnInstitution, models.DO_NOTHING)
    created_date = models.DateTimeField()
    modified_date = models.DateTimeField()
    active = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'wn_selected_course'
        unique_together = (('user', 'course', 'institution'),)
