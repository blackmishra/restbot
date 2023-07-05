from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import time


class Resy(models.Model):
    task = models.CharField(max_length=180)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False, blank=True)
    completed = models.BooleanField(default=False, blank=True)
    updated = models.DateTimeField(auto_now=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.task


class User(models.Model):
    user_email = models.CharField(
        max_length=180, null=False, default="abc@email.com", primary_key=True
    )
    resy_email = models.CharField(max_length=180, null=False, default="abc@email.com")
    resy_pwd = models.CharField(max_length=180, null=False, default="abc")
    user_name = models.CharField(max_length=180, null=False, default="abc")
    user_token = models.TextField(default="abc")
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Name:{self.user_name}, Email: {self.user_email}"


class Restaurant(models.Model):
    rest_name = models.CharField(max_length=180, null=False, blank=False)
    rest_id = models.IntegerField(primary_key=True, default=0)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.rest_name


class Reservation_request(models.Model):
    user_email = models.ForeignKey(
        User, on_delete=models.CASCADE, default="abc@email.com"
    )
    booking_id = models.TextField(default="abc")
    rest_name = models.CharField(max_length=180, null=False)
    rest_id = models.IntegerField(null=False, blank=False)
    date = models.DateField(null=False, blank=False)
    from_time = models.TimeField(default=time(8, 0))
    to_time = models.TimeField(default=time(8, 0))
    number_of_guests = models.IntegerField(null=False, blank=False)
    booking_available_till = models.DateField(null=False, blank=False)
    is_booking_date_active = models.BooleanField(default=False)
    booking_status = models.CharField(max_length=100, null=False, default="Pending")

    def __str__(self):
        booking_desc = (
            f"Booking of {self.number_of_guests} at {self.rest_name} on {self.date}"
        )
        return booking_desc

    def get_date_diff(self, date):
        # today = date.today()
        diff = self.date - self.booking_available_till
        return diff.days

    @property
    def is_booking_date_available(self):
        days_remaining = self.get_date_diff(self.date)
        if days_remaining > 1:
            print("Booking Not Active!")
            return False
        else:
            print("Booking Active")
            return True

    @property
    def remove_booking_req(self):
        days_remaining = self.get_date_diff(self.date)
        if days_remaining < 0:
            print("Booking Date is passed!")
            return True


class Booking_details(models.Model):
    booking_id = models.ForeignKey(
        Reservation_request, on_delete=models.CASCADE, blank=True, null=True
    )
    booking_status = models.CharField(max_length=100, null=False, default="Pending")
    reservation_id = models.TextField(default="abc")
    reservation_cnf_token = models.TextField(default="abc")

    def __str__(self):
        return self.booking_id
