# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class WnCourse(models.Model):
    course_name = models.CharField(max_length=200)
    course_description = models.TextField()
    stream = models.ForeignKey('WnStream', models.DO_NOTHING, db_column='stream')
    degree = models.ForeignKey('WnDegree', models.DO_NOTHING, db_column='degree')
    created_date = models.DateTimeField()
    modified_date = models.DateTimeField()
    active = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'wn_course'


class WnCourseChoice(models.Model):
    user = models.ForeignKey('WnUser', models.DO_NOTHING, db_column='user')
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


class WnDistrict(models.Model):
    name = models.CharField(max_length=500, blank=True, null=True)
    state = models.ForeignKey('WnState', models.DO_NOTHING, db_column='state')
    created_date = models.DateTimeField()
    modified_date = models.DateTimeField()
    active = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'wn_district'


class WnInstitution(models.Model):
    institution_name = models.CharField(max_length=500, blank=True, null=True)
    website = models.TextField(blank=True, null=True)
    institution_type = models.ForeignKey('WnInstitutionType', models.DO_NOTHING, db_column='institution_type',
                                         blank=True, null=True)
    state = models.ForeignKey('WnState', models.DO_NOTHING)
    district = models.ForeignKey(WnDistrict, models.DO_NOTHING)
    created_date = models.DateTimeField()
    modified_date = models.DateTimeField()
    active = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'wn_institution'


class WnInstitutionChoice(models.Model):
    user = models.ForeignKey('WnUser', models.DO_NOTHING)
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
                                       primary_key=True)  # The composite primary key (institution_id, course_id) found, that is not supported. The first column is selected.
    course = models.ForeignKey(WnCourse, models.DO_NOTHING)
    created_date = models.DateTimeField()
    modified_date = models.DateTimeField()
    active = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'wn_institution_course'
        unique_together = (('institution', 'course'),)


class WnInstitutionType(models.Model):
    type = models.CharField(max_length=500, blank=True, null=True)
    created_date = models.DateTimeField()
    modified_date = models.DateTimeField()
    active = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'wn_institution_type'


class WnLocationChoice(models.Model):
    user = models.ForeignKey('WnUser', models.DO_NOTHING, db_column='user')
    state = models.ForeignKey('WnState', models.DO_NOTHING, db_column='state')
    district = models.ForeignKey(WnDistrict, models.DO_NOTHING, db_column='district')
    created_date = models.DateTimeField()
    modified_date = models.DateTimeField()
    active = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'wn_location_choice'
        unique_together = (('user', 'state', 'district'),)


class WnSelectedCourse(models.Model):
    user = models.ForeignKey('WnUser', models.DO_NOTHING)
    course = models.ForeignKey(WnCourse, models.DO_NOTHING)
    institution = models.ForeignKey(WnInstitution, models.DO_NOTHING)
    created_date = models.DateTimeField()
    modified_date = models.DateTimeField()
    active = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'wn_selected_course'
        unique_together = (('user', 'course', 'institution'),)


class WnState(models.Model):
    name = models.CharField(max_length=500, blank=True, null=True)
    created_date = models.DateTimeField()
    modified_date = models.DateTimeField()
    active = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'wn_state'


class WnStream(models.Model):
    stream_name = models.CharField(max_length=500, blank=True, null=True)
    created_date = models.DateTimeField()
    modified_date = models.DateTimeField()
    active = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'wn_stream'


class WnStreamChoice(models.Model):
    user = models.ForeignKey('WnUser', models.DO_NOTHING, db_column='user')
    stream = models.ForeignKey(WnStream, models.DO_NOTHING, db_column='stream')
    created_date = models.DateTimeField()
    modified_date = models.DateTimeField()
    active = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'wn_stream_choice'
        unique_together = (('user', 'stream'),)


class WnUser(models.Model):
    user_name = models.CharField(max_length=255)
    hsc_percentage = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    user_gender = models.CharField(max_length=20)
    school_passed_out_year = models.IntegerField()
    studied_institution_type = models.IntegerField(blank=True, null=True)
    state = models.ForeignKey(WnState, models.DO_NOTHING, db_column='state')
    district = models.ForeignKey(WnDistrict, models.DO_NOTHING, db_column='district')
    created_date = models.DateTimeField()
    modified_date = models.DateTimeField()
    active = models.CharField(max_length=1)
    email = models.CharField(max_length=250, blank=True, null=True)
    password = models.CharField(max_length=255)
    profile_picture = models.CharField(max_length=255, blank=True, null=True)
    stream = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'wn_user'


class WnContact(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} - {self.subject}"

    class Meta:
        managed = False
        db_table = 'wn_contact'
