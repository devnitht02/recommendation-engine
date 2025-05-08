# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.contrib.auth.models import User
from django.db import models
from users.models import WnUser
from institutions.models import WnCourse, WnInstitution, WnStream


class WnSelectedCourse(models.Model):
    user = models.ForeignKey(WnUser, models.DO_NOTHING, related_name="user_course")
    course = models.ForeignKey(WnCourse, models.DO_NOTHING, related_name="selected_course")
    institution = models.ForeignKey(WnInstitution, models.DO_NOTHING, related_name="selected_institution")
    created_date = models.DateTimeField()
    modified_date = models.DateTimeField()
    active = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'wn_selected_course'
        unique_together = (('user', 'course', 'institution'),)


class WnStreamChoice(models.Model):
    user = models.ForeignKey(WnUser, models.DO_NOTHING, db_column='user', related_name="user_stream")
    stream = models.ForeignKey(WnStream, models.DO_NOTHING, db_column='stream', related_name="user_choice")
    created_date = models.DateTimeField()
    modified_date = models.DateTimeField()
    active = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'wn_stream_choice'
        unique_together = (('user', 'stream'),)


class WnContact(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} - {self.subject}"

    class Meta:
        managed = False
        db_table = 'wn_contact'


class WnFavourite(models.Model):
    user = models.ForeignKey(WnUser, models.DO_NOTHING, db_column='user', related_name="user_favourite")
    course = models.ForeignKey(WnCourse, models.DO_NOTHING, db_column='course', blank=True, null=True)
    institution = models.ForeignKey(WnInstitution, models.DO_NOTHING, db_column='institution', blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    active = models.CharField(max_length=1, default='Y')

    class Meta:
        managed = False
        db_table = 'wn_favourite'
        unique_together = (
            ('user', 'course'),
            ('user', 'institution'),
        )

    def __str__(self):
        if self.course:
            return f"{self.user.user_name} → Course: {self.course.course_name}"
        elif self.institution:
            return f"{self.user.user_name} → Institution: {self.institution.institution_name}"
        return f"{self.user.user_name} → Unknown"
