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
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    user_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, blank=True, null=True)
    password = models.CharField(max_length=255, null=False, blank=False)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True)
    user_gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True, null=True)

    # Academic details
    stream = models.CharField(max_length=255, blank=True, null=True)
    hsc_percentage = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    school_passed_out_year = models.PositiveIntegerField(blank=True, null=True)
    studied_institution_type = models.CharField(max_length=50, blank=True, null=True)
    institution = models.CharField(max_length=255, blank=True, null=True)

    # Location details
    state = models.ForeignKey(WnState, models.DO_NOTHING, db_column='state')
    district = models.ForeignKey(WnDistrict, models.DO_NOTHING, db_column='district')

    # Metadata
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    active = models.CharField(max_length=1)

    def __str__(self):
        return self.user_name

    class Meta:
        db_table = 'wn_user'

