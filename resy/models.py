from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date


class Resy(models.Model):
    task = models.CharField(max_length = 180)
    timestamp = models.DateTimeField(auto_now_add = True, auto_now = False, blank = True)
    completed = models.BooleanField(default = False, blank = True)
    updated = models.DateTimeField(auto_now = True, blank = True)
    user = models.ForeignKey(User, on_delete = models.CASCADE, blank = True, null = True)

    def __str__(self):
        return self.task
    

class Restaurant(models.Model):
    rest_name = models.CharField(max_length = 180, null=False, blank=False)
    rest_id = models.IntegerField(null=False, blank=False)
    updated_at = models.DateTimeField(auto_now = True)
    created_at = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return self.rest_name


class Reservation_request(models.Model):
    rest_name = models.CharField(max_length = 180)
    rest_id = models.IntegerField(default=0, null=False, blank=False)
    date = models.DateField(null=False, blank=False)
    number_of_guests = models.IntegerField(null=False, blank=False)
    booking_available_till = models.DateField(null=False, blank=False)
    is_booking_date_active = models.BooleanField(default=False)

    def __str__(self):
        return self.rest_name
    
    def get_date_diff(self, date):
        # today = date.today()
        diff = self.date - self.booking_available_till
        return diff.days
    
    @property
    def is_booking_date_available(self):
        days_remaining = self.get_date_diff(self.date)
        if days_remaining>1:
            print("Booking Not Active!")
            return False
        else:
            print("Booking Active")
            return True
        
    @property
    def remove_booking_req(self):
        days_remaining = self.get_date_diff(self.date)
        if days_remaining<0:
            print("Booking Date is passed!")
            return True
        
    
class Licenses_wo_add(models.Model):
    business_legal_name = models.CharField(max_length = 180, null=True, blank=True)
    state_license_number = models.CharField(max_length = 180, null=True, blank=True)
    raw_license_type = models.CharField(max_length = 180, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    business_phone = models.CharField(max_length = 180, null=True, blank=True)
    business_email = models.CharField(max_length = 180, null=True, blank=True)
    status = models.CharField(max_length = 180, null=True, blank=True)
    state = models.CharField(max_length = 180, null=True, blank=True)
    rec_med = models.CharField(max_length = 180, null=True, blank=True)
    cultivation_license_type = models.CharField(max_length = 180, null=True, blank=True)
    med_num_patients = models.IntegerField(null=True, blank=True)
    proposed_sf = models.IntegerField(null=True, blank=True)
    state_population = models.IntegerField(null=True, blank=True)
    updated_at = models.DateField()

    class Meta:
        managed = False
        db_table = 'lic_wo_addresses'