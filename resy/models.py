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
    rest_id = models.IntegerField(primary_key=True, default=0)
    updated_at = models.DateTimeField(auto_now = True)
    created_at = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return self.rest_name


class Reservation_request(models.Model):
    rest_name = models.CharField(max_length = 180, null=False)
    rest_id = models.IntegerField(null=False, blank=False)
    date = models.DateField(null=False, blank=False)
    number_of_guests = models.IntegerField(null=False, blank=False)
    booking_available_till = models.DateField(null=False, blank=False)
    is_booking_date_active = models.BooleanField(default=False)
    user_token = models.TextField(default='abc')
    resy_email = models.CharField(max_length = 180, null=False, default='abc')
    resy_pwd = models.CharField(max_length = 180, null=False, default='abc')
    booking_status = models.CharField(max_length = 100, null=False, default='Pending')

    def __str__(self):
        booking_desc = f"Booking of {self.number_of_guests} at {self.rest_name} on {self.date}"
        return booking_desc
    
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
        
    


