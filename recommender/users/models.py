from django.db import models


class WnDistrict(models.Model):
    name = models.CharField(max_length=500, blank=True, null=True)
    state = models.ForeignKey('WnState', models.DO_NOTHING, db_column='state')
    created_date = models.DateTimeField()
    modified_date = models.DateTimeField()
    active = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'wn_district'


class WnState(models.Model):
    name = models.CharField(max_length=500, blank=True, null=True)
    created_date = models.DateTimeField()
    modified_date = models.DateTimeField()
    active = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'wn_state'


class WnUser(models.Model):
    user_name = models.CharField(max_length=255)
    hsc_percentage = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    date_of_birth = models.DateField(null=True, default=None)
    user_gender = models.CharField(max_length=20)
    school_passed_out_year = models.IntegerField(null=True, default=None)
    studied_institution_type = models.IntegerField(blank=True, null=True)
    state = models.ForeignKey(WnState, models.DO_NOTHING, db_column='state')
    district = models.ForeignKey(WnDistrict, models.DO_NOTHING, db_column='district')
    created_date = models.DateTimeField()
    modified_date = models.DateTimeField()
    active = models.CharField(max_length=1)
    email = models.CharField(max_length=250, blank=True, null=True)
    password = models.CharField(max_length=255)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    stream = models.CharField(max_length=255, blank=True, null=True)
    last_login = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'wn_user'
